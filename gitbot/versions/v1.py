from types import SimpleNamespace
from sanic import Blueprint
from gitbot.auth import verify_token

# Routes for /v1/ api version with required authentication
import gitbot.bots

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

    @property
    def blueprint(self):
        return self._blueprint

    @blueprint.setter
    def blueprint(self, value):
        self._blueprint = value


# def v1(database):
#     gitbot.bots.bots.db = database


v1 = Version()

# Database to be used for this version of API
# gitbot.bots.db = v1.database
# gitbot.bots.bots.db = v1.database


# from gitbot.bots import bot

# endpoints with required authentication
auth_group = Blueprint.group(gitbot.bots.bot, gitbot.bots.bots)

# Add required JWT authentication to this group
auth_group.middleware("request")(verify_token)

# version1 = Blueprint.group(auth_group, url_prefix="/v1")
# version1 = Blueprint.group(auth_group, url_prefix="/v1")

v1.blueprint = Blueprint.group(auth_group, url_prefix="/v1") 