from enum import Enum
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Mapping
from pydantic import BaseModel, validator


class MongoIssueActionStatus(str, Enum):
    mark_stale = 'mark_stale'
    close_issue = 'close_issue'

    class Config:
        use_enum_values = True


class MongoIssueAction(BaseModel):
    status: MongoIssueActionStatus
    date: datetime


class MongoIssue(BaseModel):
    issue: int
    repo: str
    owner: str
    installation_id: int
    action: MongoIssueAction

    @staticmethod
    def new_from(issue: int, repo: str, owner: str, installation_id: int):
        utcnow = datetime.utcnow()
        print(f"Current datetime: [{utcnow}]")
        stale_date = utcnow + timedelta(minutes=1)
        print(f"Stale datetime: [{stale_date}]")

        action = MongoIssueAction(
            status=MongoIssueActionStatus.mark_stale,
            date=stale_date
        )

        return MongoIssue(
            issue=issue,
            repo=repo,
            owner=owner,
            installation_id=installation_id,
            action=action
        )
