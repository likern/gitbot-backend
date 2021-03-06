from sanic import response
from pydantic import BaseModel
from githook import GitHub, NoneContext

from pymongo.errors import DuplicateKeyError
from models import mongo
from models.github.installation import (
    InstallationCreated,
    InstallationDeleted,
    InstallationNewPermissions
)

from models.github.issue import IssueEvent, IssueOpened, IssueClosed, IssueEdited
from models.mongo.user import MongoUserAuthStatus

webhook = GitHub(None, context=NoneContext())

@webhook.middleware(IssueEvent)
async def issue_event(issue: IssueEvent):
    result = await webhook.db.github.events.insert_one(issue.dict())
    if not result.acknowledged:
        # FIXME: Handle error
        pass

    print(f"[GITHUB] EVENT ISSUE WAS LOGGED WITH ID: [{result.inserted_id}]")
    return response.json({}, status=200)


@webhook.handler(InstallationCreated)
async def installation_created(event: InstallationCreated):
    print("[GITHUB] [WEBHOOK] [INSTALLATION CREATED]")
    print(event.to_string(pretty=True))

    # Identify installation id with user token
    account_id = event.installation.account.id
    installation_id = event.installation.id

    user = await webhook.db.telegram.users.find_one(
        filter={
            "auth.status": MongoUserAuthStatus.success,
            "auth.github.user_id": account_id
        },
        projection=["auth.token"]
    )
    print(user)
    try:
        result = await webhook.db.telegram.installations.insert_one({
            "_id": installation_id, "token": user["auth"]["token"]
        })
    except DuplicateKeyError:
        # Probably it's second weebhook call
        # for the same installation event
        # Ignore it
        print(f"[DuplicateKeyError] Installation with id [{installation_id}]. Ignore it.")

    return response.json({}, status=200)


@webhook.handler(IssueOpened)
async def issue_opened(event: IssueOpened):
    print(
        "[GIHUB] [WEBHOOK] [ISSUE OPENED] "
        f"Number: [{event.issue.number}], "
        f"Repo: [{event.repository.name}], "
        f"Owner: [{event.repository.owner.login}], "
        f"Install Id: [{event.installation.id}]"
    )
    # print(event.to_string(pretty=True))

    # result = await webhook.db.github.issues.insert_one(
    #     event.dict(skip_defaults=True)
    # )
    # if not result.acknowledged:
    #     # FIXME: Handle error
    #     pass

    issue = mongo.MongoIssue.new_from(
        issue=event.issue.number,
        repo=event.repository.name,
        owner=event.repository.owner.login,
        installation_id=event.installation.id
    )

    result = await webhook.db.telegram.issues.insert_one(
        issue.dict(skip_defaults=True)
    )
    if not result.acknowledged:
        # FIXME: Handle error
        pass
    

    print(f"[GITHUB] ISSUE WAS OPENED WITH ID: [{result.inserted_id}]")
    return response.json({}, status=200)


@webhook.handler(IssueClosed)
async def issue_closed(event: IssueClosed, set_context):
    print("[GIHUB] [WEBHOOK] [ISSUE CLOSED]")
    # print(event.to_string(pretty=True))
    return response.json({}, status=200)

@webhook.handler(IssueEdited)
async def issue_edited(event: IssueEdited, set_context):
    print("[GIHUB] [WEBHOOK] [ISSUE EDITED]")
    # print(event.to_string(pretty=True))

    return response.json({}, status=200)
