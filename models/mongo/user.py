import uuid
from enum import Enum
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Mapping
from pydantic import BaseModel, UUID4, validator
from models import telegram


class MongoUserGithubLinking(str, Enum):
    not_linked = 'not_linked'
    linked = 'linked'


class MongoUserMetadata(BaseModel):
    link_status: MongoUserGithubLinking


class MongoUserNotLinked(MongoUserMetadata):
    state: str
    link_status: MongoUserGithubLinking = MongoUserGithubLinking.not_linked

    class Config:
        use_enum_values = True


class MongoUserLinked(MongoUserMetadata):
    code: str
    link_status: MongoUserGithubLinking = MongoUserGithubLinking.linked

    class Config:
        use_enum_values = True


class MongoUser(BaseModel):
    data: Any
    metadata: Union[MongoUserNotLinked, MongoUserLinked]

    @staticmethod
    def new_from(data: telegram.User):
        if not isinstance(data, telegram.User):
            raise TypeError(
                f'data should be of [telegram.User] type')

        metadata = MongoUserNotLinked(
            state=str(uuid.uuid4()),
            link_status=MongoUserGithubLinking.not_linked
        )
        return MongoUser.parse_obj({
            'data': data,
            'metadata': metadata
        })


class ProjectionMongoUserNotLinked(BaseModel):
    _id: Any
    metadata: MongoUserNotLinked


class ProjectionMongoUserLinked(BaseModel):
    _id: Any
    metadata: MongoUserLinked
