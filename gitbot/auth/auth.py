from sanic.exceptions import Unauthorized

from firebase_admin import auth
from firebase_admin.auth import AuthError

async def verify_token(request):
  try:
    jwt_info = auth.verify_id_token(request.token)
    request['user_id'] = jwt_info["user_id"]
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