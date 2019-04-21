from sanic import Sanic
from sanic import response
import asyncio
import subprocess
from datetime import timedelta
import aiohttp
import helpers
from decorators import mongodb
from motor import motor_asyncio
from emoji import emojize
# from models.message import Message, TextMessage, User
# from models.update import Update
from models import github, mongo, telegram
from types import SimpleNamespace
from api.telegram import Telegram
import pprint
import json

from bson.objectid import ObjectId

app = Sanic(__name__)
app.config.from_envvar('HELVYBOT_CONFIG')

api = None
db = SimpleNamespace(
    telegram=None,
    github=None
)


@app.listener('before_server_start')
async def init(app, loop):
    app.clients = SimpleNamespace(
        github=helpers.get_aiohttp_client_for_github(
            jwt_token=app.config.GITHUB_GWT_TOKEN, loop=loop),
        telegram=aiohttp.ClientSession(loop=loop),
        mongodb=motor_asyncio.AsyncIOMotorClient(app.config.MONGO_CONNECTION)
    )

    telegram = Telegram(token=app.config.TELEGRAM_TOKEN,
                        client=app.clients.telegram)

    database = SimpleNamespace(
        telegram=app.clients.mongodb["helvybot"],
        github=app.clients.mongodb["github"]
    )

    global api
    global db

    db.telegram = SimpleNamespace(
        updates=database.telegram['updates'],
        users=database.telegram['users'],
        logs=database.telegram['logs']
    )

    db.github = SimpleNamespace(
        issues=database.github['issues']
    )

    api = SimpleNamespace(
        telegram=telegram
    )


@app.listener('after_server_stop')
async def finish(app, loop):
    await app.clients.github.close()
    await app.clients.telegram.close()
    await app.clients.mongodb.close()
    loop.close()


@app.route("/", methods=['GET'])
async def webhook(request):
    return response.json({}, status=200)


async def create_if_new_user(user):
    if user is None:
        return

    await db.telegram.users.update_one(
        {"id": user["id"]},
        {"$setOnInsert": user},
        upsert=True
    )

# FIXME: Work in progress


async def get_stale_issues(delta: timedelta):
    result = await db.github.issues.find(
        {"metadata": {'$'}},
        {"$setOnInsert": obj.dict(skip_defaults=True)},
        upsert=True
    )


async def process_text_message(message):
    if message is None:
        return None

    text_message = telegram.TextMessage.parse_obj(message)
    chat_id = text_message.chat.id
    print(f"Chat id: [{chat_id}]")
    if text_message.text == "/help":
        await api.telegram.send_message(chat_id, "Справочная информация")


def parse_github_payloads(request):
    data = request.json
    if data['issue']:
        return github.IssueEvent.parse_obj(data)


def parse_telegram_payloads(request):
    data = request.json
    if data['message']:
        message = telegram.Message.parse_obj(data['message'])
        if message.text:
            if message.text.startswith('/start'):
                return telegram.StartCommand.parse_obj(data['message'])

        # return telegram.Message.parse_obj(data)


@app.route("/github/setup_url", methods=['GET', 'POST'])
async def github_setup_url(request):
    print("[GITHUB] [SETUP URL]:")
    print(request.url)
    print("[GITHUB] [SETUP URL] QUERY PARAMS:")
    print(request.args)
    print("[GITHUB] [SETUP URL] HEADERS:")
    print(request.headers)
    print("[GITHUB] [SETUP URL] INCOMING BODY:")
    print(json.dumps(request.json, indent=2, sort_keys=True))

    # await api.telegram.send_message(telegram.SendMessage(
    #     chat_id=payload.chat.id,
    #     text="Hi there! My name is *HelvyBot* and I'll help you to automate your daily routines on *GitHub*"
    #     parse_mode=telegram.ParseMode.markdown
    # ))

    # if 'state' in request.args:
    #     state = request.args['state']

    # redirect_url = 'https://telegram.me/helvybot'
    # redirect_url = f'https://api.telegram.org/bot731461938:AAHBePXz0g-QtDTHLOHX0CqcYRm71_apgcg/sendMessage?chat_id=[CHANNEL_NAME]&text=[MESSAGE_TEXT]'
    return response.json(
        {},
        headers={'Location': redirect_url},
        status=308
    )
    # return response.json({}, status=200)

    # states = request.args['state']
    # codes = request.args['code']
    # if not(states and codes):
    #     return response.json({}, status=299)

    # if not(len(states) == 1 and len(codes) == 1):
    #     return response.json({}, status=299)

    # state = states[0]
    # code = codes[0]
    # document = await db.telegram.users.find_one(
    #     filter={
    #         "metadata.state": state,
    #         "metadata.link_status": mongo.MongoUserGithubLinking.not_linked.value
    #     },
    #     projection=["metadata"]
    # )

    # if document is None:
    #     return response.json({}, status=299)

    # object_id = document['_id']
    # # user_metadata = mongo.MongoUserNotLinked.parse_obj(document)
    # updated_metadata = mongo.MongoUserLinked(
    #     code=code,
    #     link_status=mongo.MongoUserGithubLinking.linked.value
    # )
    # result = await db.telegram.users.update_one(
    #     filter={"_id": object_id},
    #     update={
    #         "$set": {"metadata": updated_metadata.dict(skip_defaults=True)}
    #     }
    # )
    # if result.acknowledged and result.modified_count == 1:
    #     status = 200
    # else:
    #     status = 502
    # return response.json({}, status=status)


@app.route("/github/auth", methods=['GET'])
async def github_auth_webhook(request):
    print("[GITHUB] [AUTH] QUERY PARAMS:")
    print(request.args)
    print("[GITHUB] [AUTH] HEADERS:")
    print(request.headers)
    print("[GITHUB] [AUTH] INCOMING BODY:")
    print(json.dumps(request.json, indent=2, sort_keys=True))

    states = request.args['state']
    codes = request.args['code']
    if states and codes and len(states) == 1 and len(states) == 1:
        state = states[0]
        code = codes[0]
        document = await db.telegram.users.find_one(
            filter={
                "metadata.authentication.state": state,
                "metadata.authentication.link_status": mongo.MongoUserGithubLinking.not_linked.value
            },
            projection=["metadata"]
        )

        if document:
            object_id = document['_id']
            chat_id = document['metadata']['chat_id']

            updated_metadata = mongo.MongoUserLinked(
                code=code,
                link_status=mongo.MongoUserGithubLinking.linked.value
            )
            result = await db.telegram.users.update_one(
                filter={"_id": object_id},
                update={
                    "$set": {"metadata.authentication": updated_metadata.dict(skip_defaults=True)}
                }
            )
            if result.acknowledged and result.modified_count == 1:
                msg1 = telegram.SendMessage(
                    chat_id=chat_id,
                    text=emojize("*Success!* :clap:", use_aliases=True),
                    parse_mode=telegram.ParseMode.markdown
                )
                await api.telegram.send_message(msg1)
                await telegram_bots(chat_id)
            else:
                msg1 = telegram.SendMessage(
                    chat_id=chat_id,
                    text=emojize("Authorization failed :confused:",
                                 use_aliases=True),
                    parse_mode=telegram.ParseMode.markdown
                )
                await api.telegram.send_message(msg1)

    redirect_url = 'https://telegram.me/helvybot'
    return response.json(
        {},
        headers={'Location': redirect_url},
        status=308
    )

    # return response.json({}, status=status)
    # payload = parse_github_payloads(request)

    # if isinstance(payload, github.IssueEvent):
    #     if payload.action == github.IssueAction.opened:
    #         obj = mongo.MongoIssue.new_from(data=payload)
    #         result = await db.github.issues.update_one(
    #             {"data.issue.id": obj.data.issue['id']},
    #             {"$setOnInsert": obj.dict(skip_defaults=True)},
    #             upsert=True
    #         )

    #         print(f"[GITHUB] [Issues] event was saved")

    # issue_event = github.issues.IssueEvent.parse_obj(request.json)
    # update = Update.parse_obj(request.json)

    # result = await db.updates.update_one(
    #     {"update_id": update.update_id},
    #     {"$setOnInsert": update.dict(skip_defaults=True)},
    #     upsert=True
    # )
    # print(f"[GITHUB] [Issues] event was fired")
    # print(f"[GITHUB] [Issues] event was fired [{result.acknowledged}]")

    # status = None
    # if result.acknowledged:
    #     status = 200
    # else:
    #     status = 502

    # Schedule to process telegram update
    # app.add_task(process_text_message(update.message.dict(skip_defaults=True)))
    # app.add_task(process_text_message(update.message))
    # app.add_task(create_if_new_user(update.message.sender))


@app.route("/github", methods=['POST'])
async def github_webhook(request):

    print("[GITHUB] [WEBHOOK] QUERY PARAMS:")
    print(request.args)
    print("[GITHUB] [WEBHOOK] HEADERS:")
    print(request.headers)
    print("[GITHUB] [WEBHOOK] INCOMING BODY:")
    print(json.dumps(request.json, indent=2, sort_keys=True))

    return response.json({}, status=200)
    payload = parse_github_payloads(request)

    if isinstance(payload, github.IssueEvent):
        if payload.action == github.IssueAction.opened:
            obj = mongo.MongoIssue.new_from(data=payload)
            result = await db.github.issues.update_one(
                {"data.issue.id": obj.data.issue['id']},
                {"$setOnInsert": obj.dict(skip_defaults=True)},
                upsert=True
            )

            print(f"[GITHUB] [Issues] event was saved")

    # issue_event = github.issues.IssueEvent.parse_obj(request.json)
    # update = Update.parse_obj(request.json)

    # result = await db.updates.update_one(
    #     {"update_id": update.update_id},
    #     {"$setOnInsert": update.dict(skip_defaults=True)},
    #     upsert=True
    # )
    # print(f"[GITHUB] [Issues] event was fired")
    # print(f"[GITHUB] [Issues] event was fired [{result.acknowledged}]")

    status = None
    if result.acknowledged:
        status = 200
    else:
        status = 502

    # Schedule to process telegram update
    # app.add_task(process_text_message(update.message.dict(skip_defaults=True)))
    # app.add_task(process_text_message(update.message))
    # app.add_task(create_if_new_user(update.message.sender))

    return response.json({}, status=status)


@app.route("/", methods=['POST'])
async def telegram_webhook(request):
    print("TELEGRAM INCOMING WEBHOOK JSON:")
    print(json.dumps(request.json, indent=2, sort_keys=True))
    payload = parse_telegram_payloads(request)
    if isinstance(payload, telegram.StartCommand):

        obj = mongo.MongoUser.new_from(payload.sender, chat_id=payload.chat.id)
        result = await db.telegram.users.update_one(
            {"data.id": obj.data.id},
            {"$set": obj.dict(skip_defaults=True)},
            upsert=True
        )

        if not result.acknowledged:
            return response.json({}, status=500)

        msg1 = telegram.SendMessage(
            chat_id=payload.chat.id,
            text="Hi there! My name is *HelvyBot* and I'll help you to automate your daily routines on *GitHub*",
            parse_mode=telegram.ParseMode.markdown
        )
        await api.telegram.send_message(msg1)
        msg2 = telegram.SendMessage(
            chat_id=payload.chat.id,
            text="But before, I need some rights to help you",
            parse_mode=telegram.ParseMode.markdown
        )
        await api.telegram.send_message(msg2)
        await asyncio.sleep(1)

        state = obj.metadata.authentication.state
        url_button = telegram.InlineUrlButton(
            text='Authorization',
            url=f'https://github.com/login/oauth/authorize?client_id={app.config.GITHUB_CLIENT_ID}&state={state}'
        )

        # url_button = telegram.InlineUrlButton(
        #     text='Install HelvyBot',
        #     url=f'https://github.com/apps/helvybot/installations/new'
        # )
        # url_button = telegram.InlineUrlButton(
        #     text='Install HelvyBot',
        #     url=f'http://helvy.ngrok.io/auth/telegram?state={state}'
        # )

        keyboard_markup = telegram.InlineKeyboardMarkup(
            inline_keyboard=[[url_button]])
        app_github_link = telegram.SendMessage(
            chat_id=payload.chat.id,
            text='Follow this link',
            disable_web_page_preview=True,
            reply_markup=keyboard_markup
        )

        await api.telegram.send_message(app_github_link)
        # if not result.acknowledged:
        #     print(
        #         f'[FAILED] Sending message: {json.dumps(message.json, indent=2, sort_keys=True)}')
        #     return json({}, status=500)
        return response.json({}, status=200)

    # pp = pprint.PrettyPrinter(indent=2)

    # pp.pprint(request.json)
    # update = telegram.Update.parse_obj(request.json)

    # result = await db.updates.update_one(
    #     {"update_id": update.update_id},
    #     {"$setOnInsert": update.dict(skip_defaults=True)},
    #     upsert=True
    # )
    # print(f"[MONGODB] [Update] was added [{result.acknowledged}]")

    # status = None
    # if result.acknowledged:
    #     status = 200
    # else:
    #     status = 502

    # # Schedule to process telegram update
    # # app.add_task(process_text_message(update.message.dict(skip_defaults=True)))
    # app.add_task(process_text_message(update.message))
    # app.add_task(create_if_new_user(update.message.sender))

    return response.json({}, status=200)


@app.route("/auth/telegram", methods=['POST', 'GET'])
async def telegram_auth_endpoint(request):
    # Here we receive unique code state in query parameter
    # Thus we can be sure it's a valid user
    print("[TELEGRAM] [AUTH] QUERY PARAMS:")
    print(request.args)
    print("[TELEGRAM] [AUTH] HEADERS:")
    print(request.headers)
    print("[TELEGRAM] [AUTH] INCOMING BODY:")
    print(json.dumps(request.json, indent=2, sort_keys=True))

    redirect_url = 'https://github.com/apps/helvybot/installations/new?mobile=1'
    if 'state' in request.args:
        state = request.args['state']
        return response.json(
            {},
            headers={'X-HelvyBot-State': state, 'Location': redirect_url},
            status=308
        )
    return response.json({}, status=502)

    # payload = parse_telegram_payloads(request)
    # if isinstance(payload, telegram.StartCommand):

    #     obj = mongo.MongoUser.new_from(payload.sender)
    #     result = await db.telegram.users.update_one(
    #         {"data.id": obj.data.id},
    #         {"$set": obj.dict(skip_defaults=True)},
    #         upsert=True
    #     )

    #     if not result.acknowledged:
    #         return response.json({}, status=500)

    #     welcome_message = telegram.SendMessage(
    #         chat_id=payload.chat.id,
    #         text="Hello and welcome! I will help you automating time-consuming tasks in GithHub ;)"
    #     )
    #     await api.telegram.send_message(welcome_message)
    #     await asyncio.sleep(0.3)
    #     install_message = telegram.SendMessage(
    #         chat_id=payload.chat.id,
    #         text="Let's start with installing me on Github"
    #     )
    #     await api.telegram.send_message(install_message)
    #     await asyncio.sleep(0.3)

    #     state = obj.metadata.state
    #     # url_button = telegram.InlineUrlButton(
    #     #     text='Install HelvyBot on Github',
    #     #     url=f'https://github.com/login/oauth/authorize?client_id={app.config.GITHUB_CLIENT_ID}&state={state}'
    #     # )
    #     url_button = telegram.InlineUrlButton(
    #         text='Install HelvyBot',
    #         url=f'https://github.com/apps/helvybot/installations/new'
    #     )

    #     keyboard_markup = telegram.InlineKeyboardMarkup(
    #         inline_keyboard=[[url_button]])
    #     app_github_link = telegram.SendMessage(
    #         chat_id=payload.chat.id,
    #         text='Test',
    #         disable_web_page_preview=False,
    #         reply_markup=keyboard_markup
    #     )

    #     await api.telegram.send_message(app_github_link)
    #     return response.json({}, status=200)
    # return response.json({}, status=200)


async def telegram_bots(chat_id: telegram.ChatId):
    stale_button = telegram.KeyboardButton(
        text='Stale Bot')
    keyboard_markup = telegram.ReplyKeyboardMarkup(
        keyboard=[[stale_button]],
        resize_keyboard=True
    )
    config_message = telegram.SendMessage(
        chat_id=chat_id,
        text="It's time to *configure* bots. Select a bot to set up",
        parse_mode=telegram.ParseMode.markdown,
        reply_markup=keyboard_markup
    )

    await api.telegram.send_message(config_message)


async def redirect_to_github_with_custom_headers(self, *, url, state):

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            print(resp.status)
            print(await resp.text())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
