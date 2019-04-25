from pydantic import BaseModel
from githook import GitHub, NoneContext
from models import mongo
from models.github.installation import (
    InstallationCreated,
    InstallationDeleted,
    InstallationNewPermissions
)

from models.github.issue import IssueOpened, IssueClosed

webhook = GitHub(None, context=NoneContext())


@webhook.handler(msg_type=InstallationCreated)
async def installation_created(event: InstallationCreated, set_context):
    print("[GIHUB] [WEBHOOK] [INSTALLATION CREATED]")
    print(event.to_string(pretty=True))


@webhook.handler(msg_type=IssueOpened)
async def installation_created(event: IssueOpened, set_context):
    print("[GIHUB] [WEBHOOK] [ISSUE OPENED]")
    print(event.to_string(pretty=True))

    issue = mongo.MongoIssue.new_from(issue_id=event.issue['id'])
    # result = await db.telegram.issues.update_one(
    #     {"issue_id": issue.issue_id},
    #     {"$set": issue.dict(skip_defaults=True)},
    #     upsert=True
    # )
    return response.json({}, status=200)


@webhook.handler(msg_type=IssueClosed)
async def installation_created(event: IssueClosed, set_context):
    print("[GIHUB] [WEBHOOK] [ISSUE CLOSED]")
    print(event.to_string(pretty=True))
