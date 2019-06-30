from distutils import util
from sanic import Blueprint, response
from sanic.exceptions import Unauthorized, NotFound, ServerError, InvalidUsage

from firebase_admin import auth
from firebase_admin.auth import AuthError

import helpers

# This variable is initialized magically outside
db = None

bots = Blueprint('bots', url_prefix='/bots')

@bots.route("/list", methods=['GET'])
async def get_user_bots(request):
  user_id = request["user_id"]

  detailed = False
  if "detailed" in request.args:
    # Takes only the last value, which overrides previous
    detailed = util.strtobool(request.args["detailed"][-1])

  # new_bot = helpers.get_bot_settings(user_id=user_id, name=js["name"], repos=js["repositories"])
  cursor = db.bots.find(
    filter={"user_id": user_id},
    projection=None if detailed else ["_id", "name"]
  )

  limit = 30
  if "limit" in request.args:
    number = int(request.args["limit"][-1])
    if number <= 0:
      raise InvalidUsage(f"Non-positive [limit={number}] query parameter is not allowed")
    limit = number

  bots = await cursor.to_list(limit)
  obj = { "bots": bots }
  
  # from app import TestJSONEncoder
  # test_encoder = TestJSONEncoder()
  # result = test_encoder.encode(obj)
  test = response.json(obj, status=200)
  return test

  # if not res.acknowledged or res.inserted_id != user_id:
  #   raise ServerError("Failed to save bot settings into database")
  
  # return response.json({}, status=200)

  # bot = helpers.get_available_repos_for_bot()
  # return response.json(bot, status=200)

# @bot.route("/", methods=['POST'])
# async def create_bot(request):
#   user_id = request.user_id
#   new_bot = helpers.get_default_bot(user_id=user_id)
#   res = await db.gitbot.bots.insert_one(new_bot)
#   if not res.acknowledged or res.inserted_id != user_id:
#     raise ServerError("Failed to save bot settings into database")
  
#   return response.json(bot["settings"], status=200)
  



  # if user is None:
  #       user = {"_id": uid}
  #       bot = helpers.get_default_bot(user_id=uid)

  #       async with await app.clients.mongodb.start_session() as s:
  #           async with s.start_transaction():
  #               res1 = await db.helvy.bots.insert_one(bot, session=s)
  #               res2 = await db.helvy.users.insert_one(user, session=s)

  #               res1_fail = not res1.acknowledged or res1.inserted_id != uid
  #               res2_fail = not res2.acknowledged or res2.inserted_id != uid
  #               if res1_fail or res2_fail:
  #                   s.abort_transaction()
  #       return response.json({}, status=200)
  #   return response.json({}, status=403)




  # bot = await db.bots.find_one(filter={"_id": request.user_id}, projection=["settings"])

  # if not bot:
  #   raise NotFound("Bot settings wasn't found")

  # print("Bot Settings:")
  # print(bot["settings"])
  # return response.json(bot["settings"], status=200)

# Returns bot settings to create bot
@bots.route("/new", methods=['GET'])
async def get_info_for_new_bot(request):
  bot = helpers.get_available_repos_for_bot()
  return response.json(bot, status=200)

@bots.route("/new", methods=['POST'])
async def create_bot(request):

  # FIXME: Check that all passed repositories and 
  # organizations are *existing* and *valid*

  # FIXME: Add support for "future repositories" option

  user_id = request["user_id"]
  js = request.json

  new_bot = helpers.get_bot_settings(user_id=user_id, name=js["name"], repos=js["repositories"])
  res = await db.bots.insert_one(new_bot)
  if not res.acknowledged or res.inserted_id != user_id:
    raise ServerError("Failed to save bot settings into database")
  
  return response.json({}, status=200)

# @bot.route("/new", methods=['POST'])
# async def create_bot(request):
#   user_id = request.user_id

#    if user is None:
#         user = {"_id": uid}
#         bot = helpers.get_default_bot(user_id=uid)

#         async with await app.clients.mongodb.start_session() as s:
#             async with s.start_transaction():
#                 res1 = await db.helvy.bots.insert_one(bot, session=s)
#                 res2 = await db.helvy.users.insert_one(user, session=s)

#                 res1_fail = not res1.acknowledged or res1.inserted_id != uid
#                 res2_fail = not res2.acknowledged or res2.inserted_id != uid
#                 if res1_fail or res2_fail:
#                     s.abort_transaction()
#         return response.json({}, status=200)
#     return response.json({}, status=403)




  bot = helpers.get_available_repos_for_bot()
  return response.json(bot, status=200)

@bots.route("/settings", methods=['GET'])
async def settings(request):
  bot = await db.bots.find_one(filter={"_id": request.user_id}, projection=["settings"])

  if not bot:
    raise NotFound("Bot settings wasn't found")

  print("Bot Settings:")
  print(bot["settings"])
  return response.json(bot["settings"], status=200)


# @app.route("/bot/settings", methods=['GET'])
# async def signup(request):
    
#     user = await db.helvy.users.find_one(
#         filter={
#             "_id": uid
#         }
#     )

#     if user is None:
#         user = {"_id": uid}
#         bot = helpers.get_default_bot(user_id=uid)

#         async with await app.clients.mongodb.start_session() as s:
#             async with s.start_transaction():
#                 res1 = await db.helvy.bots.insert_one(bot, session=s)
#                 res2 = await db.helvy.users.insert_one(user, session=s)

#                 res1_fail = not res1.acknowledged or res1.inserted_id != uid
#                 res2_fail = not res2.acknowledged or res2.inserted_id != uid
#                 if res1_fail or res2_fail:
#                     s.abort_transaction()
#         return response.json({}, status=200)
#     return response.json({}, status=403)



# @bot.middleware('request')
# async def verify_token(request):
#   try:
#     auth.verify_id_token(request.token)
#   except AuthError as error:
#     print(error)
#     raise Unauthorized(
#       message=error.message,
#       status_code=error.code,
#       scheme="Bearer"
#     )
#   except ValueError as error:
#     print(error)
#     raise Unauthorized(
#       message="Either JWT is invalid, or App’s project ID cannot be determined",
#       scheme="Bearer"
#     )