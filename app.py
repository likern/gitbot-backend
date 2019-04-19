from sanic import Sanic
from sanic import response
import asyncio
import subprocess
from datetime import timedelta
import aiohttp
import helpers
from decorators import mongodb
from motor import motor_asyncio
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


@app.route("/github/auth", methods=['GET'])
async def github_auth_webhook(request):
    print("GITHUB INCOMING AUTH WEBHOOK:")
    print(json.dumps(request.json, indent=2, sort_keys=True))

    states = request.args['state']
    codes = request.args['code']
    if not(states and codes):
        return response.json({}, status=299)

    if not(len(states) == 1 and len(codes) == 1):
        return response.json({}, status=299)

    state = states[0]
    code = codes[0]
    document = await db.telegram.users.find_one(
        filter={
            "metadata.state": state,
            "metadata.link_status": mongo.MongoUserGithubLinking.not_linked.value
        },
        projection=["metadata"]
    )

    if document is None:
        return response.json({}, status=299)

    object_id = document['_id']
    # user_metadata = mongo.MongoUserNotLinked.parse_obj(document)
    updated_metadata = mongo.MongoUserLinked(
        code=code,
        link_status=mongo.MongoUserGithubLinking.linked.value
    )
    result = await db.telegram.users.update_one(
        filter={"_id": object_id},
        update={
            "$set": {"metadata": updated_metadata.dict(skip_defaults=True)}
        }
    )
    if result.acknowledged and result.modified_count == 1:
        status = 200
    else:
        status = 502
    return response.json({}, status=status)
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

        obj = mongo.MongoUser.new_from(payload.sender)
        result = await db.telegram.users.update_one(
            {"data.id": obj.data.id},
            {"$set": obj.dict(skip_defaults=True)},
            upsert=True
        )

        if not result.acknowledged:
            return response.json({}, status=500)

        welcome_message = telegram.SendMessage(
            chat_id=payload.chat.id,
            text="Hello and welcome! I will help you automating time-consuming tasks in GithHub ;)"
        )
        await api.telegram.send_message(welcome_message)
        await asyncio.sleep(0.3)
        install_message = telegram.SendMessage(
            chat_id=payload.chat.id,
            text="Let's start with installing me on Github"
        )
        await api.telegram.send_message(install_message)
        await asyncio.sleep(0.3)

        state = obj.metadata.state
        url_button = telegram.InlineUrlButton(
            text='Install HelvyBot on Github',
            url=f'https://github.com/login/oauth/authorize?client_id={app.config.GITHUB_CLIENT_ID}&state={state}'
        )
        keyboard_markup = telegram.InlineKeyboardMarkup(
            inline_keyboard=[[url_button]])
        app_github_link = telegram.SendMessage(
            chat_id=payload.chat.id,
            text='Test',
            disable_web_page_preview=False,
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
