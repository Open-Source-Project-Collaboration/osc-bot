from db import Base, session, engine
from sqlalchemy import Column, Integer, String


# Config model
class Config(Base):
    __tablename__ = 'config'


    # Fields
    name  = Column(String, primary_key=True)
    value = Column(String)


    # Constructor and str
    def __init__(self, name, value):
        self.name  = name
        self.value = value

    def __repr__(self):
        return f'{{"{self.name}": "{self.value}"}}'


    # Static interface
    def get(name):
        return session.query(Config).filter_by(name=name).first()

    def set(name, value):
        config = Config.get(name)

        if config:
            config.value = value
        else:
            config = Config(name, value)
            session.add(config)

        session.commit()

    def set_init(name, value):
        config = Config.get(name)
        if config != None:
            return
        Config.set(name, value)


# Create tables
Base.metadata.create_all(engine)