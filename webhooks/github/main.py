from pydantic import BaseModel
from githook import GitHub, NoneContext
from models import mongo
from models.github.installation import (
    InstallationCreated,
    InstallationDeleted,
    InstallationNewPermissions
)

from models.github.issue import IssueEvent, IssueOpened, IssueClosed, IssueEdited

webhook = GitHub(None, context=NoneContext())


@webhook.middleware(IssueEvent)
async def issue_event(issue: IssueEvent):
    result = await webhook.db.github.issues.insert_one(issue.dict(skip_defaults=True))
    if not result.acknowledged:
        # FIXME: Handle error
        pass

    print(f"[GITHUB] NEW ISSUE EVENT WAS SAVED WITH ID: [{result.inserted_id}]")


@webhook.handler(InstallationCreated)
async def installation_created(event: InstallationCreated, *args):
    print("[GIHUB] [WEBHOOK] [INSTALLATION CREATED]")
    print(event.to_string(pretty=True))

    return response.json({}, status=200)


@webhook.handler(IssueOpened)
async def installation_created(event: IssueOpened, middleware):
    print("[GIHUB] [WEBHOOK] [ISSUE OPENED]")
    print(event.to_string(pretty=True))

    # issue = mongo.MongoIssue.new_from(issue_id=event.issue['id'])

    # result = await db.telegram.issues.update_one(
    #     {"issue_id": issue.issue_id},
    #     {"$set": issue.dict(skip_defaults=True)},
    #     upsert=True
    # )
    return response.json({}, status=200)


@webhook.handler(IssueClosed)
async def installation_created(event: IssueClosed, set_context):
    print("[GIHUB] [WEBHOOK] [ISSUE CLOSED]")
    print(event.to_string(pretty=True))

@webhook.handler(IssueEdited)
async def installation_created(event: IssueEdited, set_context):
    print("[GIHUB] [WEBHOOK] [ISSUE EDITED]")
    print(event.to_string(pretty=True))

    return response.json({}, status=200)
