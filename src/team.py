from db import Base, session, engine
from sqlalchemy import Column, String, Numeric
from sqlalchemy.orm import relationship
from user import User


class Team(Base):
    __tablename__ = 'teams'
    team_name = Column(String, primary_key=True)
    role_id = Column(Numeric)  # The id of the role
    leader_role_id = Column(Numeric)
    category_id = Column(Numeric)  # The id of the category
    general_id = Column(Numeric)  # The id of the general channel
    voting_id = Column(Numeric)  # The id of the voting channel
    github_id = Column(Numeric)
    repo_id = Column(Numeric)

    users = relationship("User", order_by=User.user_id, back_populates="team", cascade="all, delete, delete-orphan")

    def __init__(self, team_name, role_id, leader_role_id, category_id, general_id, github_id, repo_id, voting_id=-1):
        self.team_name = team_name
        self.role_id = role_id
        self.leader_role_id = leader_role_id
        self.category_id = category_id
        self.general_id = general_id
        self.github_id = github_id
        self.repo_id = repo_id
        self.voting_id = voting_id

    def __repr__(self):
        return f'<Team(team_name={self.team_name}, role_id={self.role_id}, category_id={self.category_id}, ' \
               f'general_id={self.general_id}, voting_id={self.voting_id})>'

    # Static interface
    @staticmethod
    def get(team_name):
        team = session.query(Team).filter_by(team_name=team_name)
        return team if team else None

    @staticmethod
    def get_all():
        teams = session.query(Team).all()
        return teams if teams else None

    @staticmethod
    def set(team_name, role_id, leader_role_id, category_id, general_id, github_id, repo_id):
        team: Team = Team.get(team_name)
        if team:
            team.role_id = role_id
            team.leader_role_id = leader_role_id
            team.category_id = category_id
            team.general_id = general_id
        else:
            team = Team(team_name, role_id, leader_role_id, category_id, general_id, github_id, repo_id)
            session.add(team)

        session.commit()

    @staticmethod
    def set_voting_channel(team_name, voting_id):
        team: Team = Team.get(team_name)
        if not team:
            return
        team.voting_id = voting_id
        session.commit()

    @staticmethod
    def delete_voting_channel(team_name):
        team: Team = Team.get(team_name)
        if not team:
            return
        team.voting_id = -1
        session.commit()

    @staticmethod
    def delete_team(team_name):
        team = Team.get(team_name)
        if not team:
            return
        session.delete(team)
        session.commit()


Base.metadata.create_all(engine)
