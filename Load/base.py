# literally import that library
from sqlalchemy import create_engine
# This import let us work with ORM in Python
from sqlalchemy.ext.declarative import declarative_base
# Importing session
from sqlalchemy.orm import sessionmaker

# Setting up all required to run teh db
Engine = create_engine('sqlite:///newspaper.db')

Session = sessionmaker(bind=Engine)

Base = declarative_base()
