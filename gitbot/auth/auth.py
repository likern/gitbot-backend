from sanic import Blueprint, response
from sanic.exceptions import Unauthorized, ServerError
from gitbot.exceptions import UnprocessableEntity
from firebase_admin import auth
from firebase_admin.auth import AuthError

db = None

async def verify_token(request):
  try:
    jwt_info = auth.verify_id_token(request.token)
    user_id = jwt_info["user_id"]
    if not user_id:
      raise ValueError("Token doesn't contain user identification")
    request['user_id'] = user_id
  except AuthError as error:
    print(error)
    raise Unauthorized(
      message=error.message,
      status_code=error.code,
      scheme="Bearer"
    )
  except ValueError as error:
    print(error)
    raise Unauthorized(
      message="Either JWT is invalid, or App’s project ID cannot be determined",
      scheme="Bearer"
    )

blueprint = Blueprint('auth')
@blueprint.route("/signup", methods=['POST'])
async def signup(request):
    user_id = request["user_id"]
    user = await db.users.find_one(
        filter={
            "_id": user_id
        }
    )

    if user is not None:
      raise UnprocessableEntity("User is already registered")

    res = await db.users.insert_one({"_id": user_id, "installed": False })
    if not res.acknowledged or res.inserted_id != user_id:
        raise ServerError("Failed to singup a new user")
    return response.json({}, status=200)