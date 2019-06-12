from sanic import Blueprint, response
from sanic.exceptions import Unauthorized, NotFound, ServerError

from firebase_admin import auth
from firebase_admin.auth import AuthError

import helpers

# This variable is initialized magically outside
global db

bot = Blueprint('bot', url_prefix='/bot')

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
@bot.route("/new", methods=['GET'])
async def get_info_for_new_bot(request):
  bot = helpers.get_available_repos_for_bot()
  return response.json(bot, status=200)

@bot.route("/new", methods=['POST'])
async def create_bot(request):
  #FIXME: Check that all passed repositories and 
  # organizations are *existing* and *valid*
  user_id = request["user_id"]
  js = request.json

  new_bot = helpers.get_bot_settings(user_id=user_id, name=js["name"], repos=js["repos"])
  res = await db.gitbot.bots.insert_one(new_bot)
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

@bot.route("/settings", methods=['GET'])
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