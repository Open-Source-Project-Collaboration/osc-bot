from db import Base, session, engine
from sqlalchemy import Column, String


# Config model
class Config(Base):
    __tablename__ = 'config'

    # Fields
    name = Column(String, primary_key=True)
    value = Column(String)

    # Constructor and str
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{{"{self.name}": "{self.value}"}}'

    # Static interface
    @staticmethod
    def get(name):
        config = session.query(Config).filter_by(name=name).first()
        return config.value if config else None

    @staticmethod
    def get_key(name):
        config = session.query(Config).filter_by(name=name).first()
        return config if config else None

    @staticmethod
    def set(name, value):
        config = Config.get_key(name)

        if config:
            config.value = value
        else:
            config = Config(name, value)
            session.add(config)

        session.commit()

    @staticmethod
    def set_init(name, value):
        config = Config.get(name)
        if config:
            return
        Config.set(name, value)

    @staticmethod
    def channels():
        chans = session.query(Config).all()
        chans = filter(lambda chan: chan.name.endswith('-channel'), chans)

        diction = {}
        for chan in chans:
            diction[chan.name] = chan.value

        return diction


# Create tables
Base.metadata.create_all(engine)
