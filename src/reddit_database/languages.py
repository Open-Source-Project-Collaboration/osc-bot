from db import Base, session, engine
from sqlalchemy import Column, String, Integer


# The language model: each language can have multiple subreddits
class Language(Base):
    __tablename__ = 'languages'

    unique_id = Column(Integer, primary_key=True)
    name = Column(String)
    subreddit = Column(String)

    # Constructor and str
    def __init__(self, name, subreddit):
        self.name = name
        self.subreddit = subreddit

    def __repr__(self):
        return f'<Language(unique_id={self.unique_id}, name={self.name}, subreddit={self.subreddit})>'

    # Static interface
    @staticmethod
    def get_all_subreddits(name):  # Gets all the subreddits of a language with a certain name
        languages = session.query(Language).filter_by(name=name).all()
        return languages if languages else None

    @staticmethod
    def get(name, subreddit):  # Gets a language with a certain subreddit
        language = session.query(Language).filter_by(name=name).filter_by(subreddit=subreddit).first()
        return language if language else None

    @staticmethod
    def set(name, subreddit):  # Sets a language to a certain subreddit
        language = Language.get(name, subreddit)
        if language:
            return
        else:
            language = Language(name, subreddit)
            session.add(language)

        session.commit()

    @staticmethod
    def delete(language, subreddit):  # Deletes a language object from the database
        language = Language.get(language, subreddit)
        if not language:
            return
        session.delete(language)
        session.commit()


Base.metadata.create_all(engine)
