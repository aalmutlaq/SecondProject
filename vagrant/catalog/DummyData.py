from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from CreateDB import Company, Base, Employee

engine = create_engine('sqlite:///company.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# startups
company1 = Company(name="STC")

session.add(company1)
session.commit()

employee1_1 = Employee(name="Mohammed", position="IOS Developer",
                       company=company1)

session.add(employee1_1)
session.commit()


employee2_1 = Employee(name="Khalid", position="HR Officer",
                       company=company1)

session.add(employee2_1)
session.commit()


company2 = Company(name="Mobily")

session.add(company2)
session.commit()

employee1_2 = Employee(name="Abdulaziz", position="CEO",
                       company=company2)

session.add(employee1_2)
session.commit()


company3 = Company(name="Tawuniya")

session.add(company3)
session.commit()

employee1_3 = Employee(name="Abdullah", position="Senior ASQA Engineer",
                       company=company3)

session.add(employee1_3)
session.commit()


employee2_3 = Employee(name="Moshary", position="Networking Engineer",
                       company=company3)

session.add(employee2_3)
session.commit()


company4 = Company(name="Wafa Company")

session.add(company4)
session.commit()

employee1_4 = Employee(name="Ansari", position="System Analyst",
                       company=company4)

session.add(employee1_4)
session.commit()


employee2_4 = Employee(name="Norah", position="Applicaiton Support",
                       company=company4)

session.add(employee2_4)
session.commit()


print("Data Added")
