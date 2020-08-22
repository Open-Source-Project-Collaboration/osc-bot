from db import Base, session, engine
from sqlalchemy import Column, String, Integer


class User(Base):
    __tablename__ = 'users'

    # Fields
    user_id = Column(Integer)
    user_team = Column(String)
    user_github = Column(String)

    # Constructor and str
    def __init(self, user_id, user_team, user_github):
        self.user_id = user_id
        self.user_team = user_team
        self.user_github = user_github

    def __repr__(self):
        return f'<User(user_id={str(self.user_id)}, user_team={self.user_team}, user_github={self.user_github})>'

    # Static interface
    @staticmethod
    def get(user_id, user_team):
        user = session.query(User).filter_by(user_id=user_id).filter_by(user_team=user_team).first()
        return user if user else None

    @staticmethod
    def set(user_id, user_team, user_github):
        user = User.get(user_id, user_team)

        if user:
            user.user_team = user_team
            user.user_github = user_github
        else:
            user = User(user_id, user_team, user_github)
            session.add(user)

        session.commit()

    @staticmethod
    def delete(user_id, user_team):
        user = User.get(user_id, user_team)
        if user:
            session.delete(user)
            session.commit()

    @staticmethod
    def delete_team(team):
        users = session.query(User).filter_by(user_team=team).all()
        if not users:
            return
        for user in users:
            session.delete(user)
        session.commit()


Base.metadata.create_all(engine)
