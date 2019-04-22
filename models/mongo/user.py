import uuid
from enum import Enum
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Mapping
from pydantic import BaseModel, UUID4, validator
from models import telegram
from models.telegram.base_types import ChatId


class MongoUserGithubLinking(str, Enum):
    not_linked = 'not_linked'
    linked = 'linked'


class MongoUserNotLinked(BaseModel):
    state: str
    link_status: MongoUserGithubLinking = MongoUserGithubLinking.not_linked

    class Config:
        use_enum_values = True


class MongoUserLinked(BaseModel):
    code: str
    link_status: MongoUserGithubLinking = MongoUserGithubLinking.linked

    class Config:
        use_enum_values = True


class MongoUserMetadata(BaseModel):
    chat_id: ChatId
    language: str
    authentication: Union[MongoUserNotLinked, MongoUserLinked]


class MongoUser(BaseModel):
    data: Any
    metadata: MongoUserMetadata

    @staticmethod
    def new_from(user: telegram.User, chat_id: telegram.ChatId):
        if not isinstance(user, telegram.User):
            raise TypeError(
                f'data should be of [telegram.User] type')

        user_not_linked = MongoUserNotLinked(
            state=str(uuid.uuid4()),
            link_status=MongoUserGithubLinking.not_linked
        )
        metadata = MongoUserMetadata(
            chat_id=chat_id,
            authentication=user_not_linked,
            language=user.language_code
        )
        # metadata = {
        #     "authentication": user_not_linked,
        #     "chat_id": chat_id
        # }

        return MongoUser.parse_obj({
            'data': user,
            'metadata': metadata
        })


class ProjectionMongoUserNotLinked(BaseModel):
    _id: Any
    metadata: MongoUserNotLinked


class ProjectionMongoUserLinked(BaseModel):
    _id: Any
    metadata: MongoUserLinked
