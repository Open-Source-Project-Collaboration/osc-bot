from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import environ

# Create sqlalchemy engine
engine = None
env = environ.get('ENV') or 'dev'
if env == 'dev':
    engine = create_engine('sqlite:///db.sqlite3')
else:
    dbdb = environ.get('DB_DB')
    name = environ.get('DB_NAME')
    pswd = environ.get('DB_PASS')
    port = environ.get('PORT')
    print(dbdb, name, pswd, port)
    engine = create_engine(f'postgresql://{name}:{pswd}@0.0.0.0:{port}/{dbdb}')

# Create a session
session = sessionmaker(bind=engine)()

# Create base model
Base = declarative_base()
