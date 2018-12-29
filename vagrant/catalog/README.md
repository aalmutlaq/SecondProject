#Name: Abdullah ALmutlaq
#Institution: Misk-Udacity
#Course: Full Stack Nanodegree
#Instructor: Lujain Algholaiqa
#Project: Second project
#Date: 22/12/2018


#About:
The purpose of this web application is to store data and provides a list of items from different categories. These list created by user registeration using Oauth. So here we are using json endpoint web applicaiton which allow each user to reads, adds, edits and deletes data based on their login.


# Prerequisite
Python3
VB
Vagrant


# Knowledge added in this Project 
- Python
- CSS
- HTML
- OAuth
- SQLAchemy
- Flask


#How to Run
- Install Vagarnt and VB
- download the vagrant udacity repository.
- clone the repo to Project2 folder
- Script run in Project2 folder:
        - Vagrant up
        - Vagrant ssh
- go to the application directory and run the following: 
        - pip3 install flask
        - pip3 install requests 
        - pip3 install sqlalchmey
        - python3 CreatedDB.py
        - python3 DummyData.py
        - python3 catalog.py

- Access and test your application by visiting [http://localhost:8000]

# Get JSON Endpoint
- Get List of all categories 
    http://localhost:8000/companies/json/

- Get list of employees by company ID
    http://localhost:8000/companies/Emp/1/json

- Get all Companies and Employees
    http://localhost:8000/companies/EmpList/json


