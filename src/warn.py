from db import Base, session, engine
from sqlalchemy import Column, Integer


class Warn(Base):
    __tablename__ = 'warns'

    user_id = Column(Integer, primary_key=True)
    warns = Column(Integer)

    def __init__(self, user_id, warns):
        self.user_id = user_id
        self.warns = warns

    def __repr__(self):
        return f'User by id {str(self.user_id)} has {str(self.warns)} warns.'

    @staticmethod
    def get(user_id):
        user = session.query(Warn).filter_by(user_id=user_id).first()
        return user if user else None

    @staticmethod
    def warn(user_id):
        user = Warn.get(user_id)
        if user:
            user.warns += 1
        else:
            user = Warn(user_id, 1)
            session.add(user)

        session.commit()

    @staticmethod
    def delete(user_id):
        user = Warn.get(user_id)
        if user:
            session.delete(user)
            session.commit()

    @staticmethod
    def warnings(user_id):
        user = Warn.get(user_id)
        return user.warns if user else 0


Base.metadata.create_all(engine)
