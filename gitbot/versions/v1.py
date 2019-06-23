from types import SimpleNamespace
from sanic import Blueprint
# from gitbot.auth.auth import verify_token

# Routes for /v1/ api version with required authentication
import gitbot.bots.bot
import gitbot.bots.bots
import gitbot.auth.auth

class Version:
    def __init__(self):
        self._blueprint = None
        self._database = None
    
    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, value):
        self._database = value
        gitbot.bots.bot.db = self._database
        gitbot.bots.bots.db = self._database
        gitbot.auth.auth.db = self._database

    @property
    def blueprint(self):
        return self._blueprint

    @blueprint.setter
    def blueprint(self, value):
        self._blueprint = value


v1 = Version()

# endpoints with required authentication
with_auth = Blueprint.group(
    gitbot.auth.auth.blueprint,
    gitbot.bots.bot.bot,
    gitbot.bots.bots.bots
)

# Add required JWT authentication to this group
with_auth.middleware("request")(gitbot.auth.auth.verify_token)

v1.blueprint = Blueprint.group(with_auth, url_prefix="/v1") 
