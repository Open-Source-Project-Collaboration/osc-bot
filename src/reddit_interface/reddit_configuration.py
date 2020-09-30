from os import path, environ

from dotenv import load_dotenv

dotenv_path = path.join(path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

client_id = environ.get("CLIENT_ID")
client_secret = environ.get("CLIENT_SECRET")
password = environ.get("REDDIT_PASSWORD")
username = environ.get("REDDIT_USERNAME")
USER_AGENT = f"discord:OSC (by u/{username})"
