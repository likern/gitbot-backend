from enum import Enum
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Mapping
from pydantic import BaseModel, validator
from models import github


class MongoIssueMetadata(BaseModel):
    when_stale: datetime

    @validator('when_stale')
    def check_datetime_is_utc(cls, value):
        return value


class MongoIssue(BaseModel):
    data: Any
    metadata: Optional[MongoIssueMetadata]

    @staticmethod
    def new_from(*, data: github.IssueEvent, metadata: MongoIssueMetadata = None):
        if metadata is None:
            stale_date = datetime.utcnow() + timedelta(minutes=1)
            metadata = {'when_stale': stale_date}

        if not isinstance(data, github.IssueEvent):
            raise TypeError(
                f'data should be of [github.IssueEvent] type')

        return MongoIssue.parse_obj({
            'data': data,
            'metadata': metadata
        })
