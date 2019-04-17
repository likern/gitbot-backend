from sanic import Sanic
from sanic.response import json
import asyncio
import subprocess
import aiohttp
import helpers
from decorators import mongodb
from motor import motor_asyncio
from models.message import Message, TextMessage, User
from models.update import Update
from models import github, mongo
from types import SimpleNamespace
from api.telegram import Telegram

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
    return json({}, status=200)


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

    text_message = TextMessage.parse_obj(message)
    chat_id = text_message.chat.id
    print(f"Chat id: [{chat_id}]")
    if text_message.text == "/help":
        await api.telegram.send_message(chat_id, "Справочная информация")


def parse_github_payloads(request):
    data = request.json
    if data['issue']:
        return github.IssueEvent.parse_obj(data)


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

    return json({}, status=status)


@app.route("/", methods=['POST'])
async def telegram_webhook(request):
    update = Update.parse_obj(request.json)

    result = await db.updates.update_one(
        {"update_id": update.update_id},
        {"$setOnInsert": update.dict(skip_defaults=True)},
        upsert=True
    )
    print(f"[MONGODB] [Update] was added [{result.acknowledged}]")

    status = None
    if result.acknowledged:
        status = 200
    else:
        status = 502

    # Schedule to process telegram update
    # app.add_task(process_text_message(update.message.dict(skip_defaults=True)))
    app.add_task(process_text_message(update.message))
    app.add_task(create_if_new_user(update.message.sender))

    return json({}, status=status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
