from sanic import response
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
    result = await webhook.db.github.events.insert_one(issue.dict(skip_defaults=True))
    if not result.acknowledged:
        # FIXME: Handle error
        pass

    print(f"[GITHUB] EVENT ISSUE WAS LOGGED WITH ID: [{result.inserted_id}]")


@webhook.handler(InstallationCreated)
async def installation_created(event: InstallationCreated):
    print("[GIHUB] [WEBHOOK] [INSTALLATION CREATED]")
    print(event.to_string(pretty=True))

    return response.json({}, status=200)


@webhook.handler(IssueOpened)
async def issue_opened(event: IssueOpened):
    print("[GIHUB] [WEBHOOK] [ISSUE OPENED]")
    print(event.to_string(pretty=True))

    result = await webhook.db.github.issues.insert_one(
        event.dict(skip_defaults=True)
    )
    if not result.acknowledged:
        # FIXME: Handle error
        pass

    issue = mongo.MongoIssue.new_from(
        issue_id=event.issue.id,
        repo_id=event.repository.id,
        owner_id=event.repository.owner.id,
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
    print(event.to_string(pretty=True))

@webhook.handler(IssueEdited)
async def issue_edited(event: IssueEdited, set_context):
    print("[GIHUB] [WEBHOOK] [ISSUE EDITED]")
    print(event.to_string(pretty=True))

    return response.json({}, status=200)
