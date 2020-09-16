from sqlalchemy.orm import relationship

from db import Base, session, engine
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey


# The user model: a user can have multiple GitHub usernames for different teams but one GitHub username for the same
# team
class User(Base):
    __tablename__ = 'users'

    # Fields
    unique_id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    user_team = Column(String, ForeignKey("teams.team_name"))
    user_github = Column(String)  # To be deleted
    user_github_id = Column(BigInteger)  # Use this in the code

    team = relationship("Team", back_populates="users")

    # Constructor and str
    def __init__(self, user_id, user_team, user_github, user_github_id):
        self.user_id = user_id
        self.user_team = user_team
        self.user_github = user_github
        self.user_github_id = user_github_id

    def __repr__(self):
        return f'<User(user_id={str(self.user_id)}, user_team={self.user_team}, user_github={self.user_github})>'

    # Static interface
    @staticmethod
    def get(user_id, user_team):
        user = session.query(User).filter_by(user_id=user_id).filter_by(user_team=user_team).first()
        return user if user else None

    @staticmethod
    def get_teams():
        return session.query(User).all()

    @staticmethod
    def get_team(user_team):
        team = session.query(User).filter_by(user_team=user_team).all()
        return team if team else None

    @staticmethod
    def set(user_id, user_team, user_github, user_github_id):
        user = User.get(user_id, user_team)

        if user:
            user.user_team = user_team
            user.user_github = user_github
            user.user_github_id = user_github_id
        else:
            user = User(user_id, user_team, user_github, user_github_id)
            session.add(user)

        session.commit()

    @staticmethod
    def set_init(user_id, user_team, user_github, user_github_id):
        user = User.get(user_id, user_team)
        if user:
            return
        else:
            User.set(user_id, user_team, user_github, user_github_id)

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
