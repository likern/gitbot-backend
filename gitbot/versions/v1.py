from types import SimpleNamespace
from sanic import Blueprint
from gitbot.auth import verify_token

# Routes for /v1/ api version with required authentication
import gitbot.bots

v1 = SimpleNamespace(
    blueprint=None,
    database=None
)

# Database to be used for this version of API
gitbot.bots.db = v1.database


# from gitbot.bots import bot

# endpoints with required authentication
auth_group = Blueprint.group(gitbot.bots.bot)

# Add required JWT authentication to this group
auth_group.middleware("request")(verify_token)

# version1 = Blueprint.group(auth_group, url_prefix="/v1")
# version1 = Blueprint.group(auth_group, url_prefix="/v1")

v1.blueprint = Blueprint.group(auth_group, url_prefix="/v1") 