from flask import Flask, render_template, request,\
    redirect, url_for, flash, make_response, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from CreateDB import Base, Company, Employee, User
from sqlalchemy.pool import SingletonThreadPool
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import json
import random
import string
import httplib2
import requests

# Instance, every time it runs create instance name
app = Flask(__name__)
engine = create_engine(
    'sqlite:///company.db?check_same_thread=False',
    poolclass=SingletonThreadPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('google_client_secret.json', 'r').read())[
    'web']['client_id']


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invaild state parameter'), 401)
        response.headers['Content-Type'] != 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets(
            'google_client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = json.loads(oauth_flow.step2_exchange(code).to_json())
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials['access_token']
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'
    gplus_id = credentials['id_token']['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID doesn't match app's."), 401)
        print("Token's client ID doesn't match app's")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already logined!'))
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials['access_token'], 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("Welcome back, %s" % login_session['username'])
    return redirect(url_for('showAllCompany'))


@app.route('/gdisconect', methods=['POST'])
def gdisconnect():
    if login_session['credentials'] is None:
        response = make_response(json.dumps(
            'Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    credentials = login_session['credentials']
    access_token = credentials['access_token']
    url = ("https://accounts.google.com/o/oauth2/revoke?token=%s"
           % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Sucessfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showAllCompany'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# Company details page


@app.route('/Company/<int:company_id>', methods=['GET', 'POST'])
def showCompany(company_id):
    company = session.query(Company).filter_by(id=company_id).one()
    employee = session.query(Employee).filter_by(company_id=company_id).all()
    if request.method == 'POST':
        if login_session.get('credentials') is None:  # position
            return redirect(url_for('login'))
        newEmployee = Employee(name=request.form['name'],
                               position=request.form['position'],
                               company_id=company_id,
                               user_id=login_session['user_id'])
        session.add(newEmployee)
        session.commit()
        flash("New employee has been added")
        return redirect(url_for('showCompany', company_id=company_id))
    else:
        return render_template('company.html',
                               company=company,
                               employee=employee)

# Main Route Has All Companies list


@app.route('/')
def showAllCompany():
    list = session.query(Company).all()
    return render_template('allList.html',
                           list=list, login_session=login_session)


# Employee Edit Page
@app.route('/Company/<int:company_id>/<int:employee_id>/edit',
           methods=['GET', 'POST'])
def editEmployee(company_id, employee_id):
    if login_session.get('credentials') is None:
        return redirect(url_for('login'))
    editEmployee = session.query(Employee).filter_by(id=employee_id).one()
    if request.method == 'POST':
        if editEmployee.user is None:
            flash("You don't have permission to do this!")
            return redirect(url_for('showCompany', company_id=company_id))
        if editEmployee.user.id != login_session['user_id']:
            flash("You don't have permission to do this!")
            return redirect(url_for('showCompany', company_id=company_id))
        if request.form['name']:
            editEmployee.name = request.form['name']
        if request.form['position']:
            editEmployee.position = request.form['position']
        session.add(editEmployee)
        session.commit()
        flash("Employee info have been updated")
        return redirect(url_for('showCompany', company_id=company_id))
    else:
        return render_template('company.html',
                               company=company, employee=employee)


# Employee Delete Page
@app.route('/Company/<int:company_id>/<int:employee_id>/delete',
           methods=['GET', 'POST'])
def deleteEmployee(company_id, employee_id):
    if login_session.get('credentials') is None:
        return redirect(url_for('login'))
    employeeToBeDeleted = session.query(
        Employee).filter_by(id=employee_id).one()
    if request.method == 'POST':
        if employeeToBeDeleted.user is None:
            flash("You don't have permission to do this!")
            return redirect(url_for('showCompany', company_id=company_id))
        if employeeToBeDeleted.user.id != login_session['user_id']:
            flash("You don't have permission to do this!")
            return redirect(url_for('showCompany', company_id=company_id))
        session.delete(employeeToBeDeleted)
        session.commit()
        flash("employee has been deleted")
        return redirect(url_for('showCompany', company_id=company_id))
    else:
        return render_template('company.html',
                               company=company, employee=employee)


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except ValueError:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    username = login_session['username']
    email = login_session['email']
    picture = login_session['picture']
    newUser = User(name=username, email=email, picture=picture)
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=email).one()
    return user.id


# Endpoint Json

@app.route('/companies/json/')
def companiesJSON():
    company = session.query(Company).all()
    return jsonify(Companies=[i.name for i in company])


@app.route('/companies/Emp/<int:company_id>/json')
def employeeByEmpIdJSON(company_id):
    company = session.query(Company).filter_by(id=company_id).all()
    employee = session.query(Employee).filter_by(company_id=company_id).all()
    return jsonify(Employees=[i.serialize for i in employee])


@app.route('/companies/EmpList/json')
def employeeListJSON():
    company = session.query(Company).all()
    employee = session.query(Employee).all()
    return jsonify(Company=[dict(c.serialize,
                   Employees=[dict(i.serialize)for i in employee])
                   for c in company])


if __name__ == '__main__':
    app.secret_key = 'super_secure'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
