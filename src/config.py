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
        config = session.query(Config).filter_by(name=name).first()
        return config.value if config else None

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

    def channels():
        chans = session.query(Config).all()
        chans = filter(lambda chan: chan.name.endswith('-channel'), chans)

        diction = {}
        for chan in chans:
            diction[chan.name] = chan.value

        return diction


# Create tables
Base.metadata.create_all(engine)