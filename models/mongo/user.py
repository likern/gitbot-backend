import uuid
from enum import Enum
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Mapping
from pydantic import BaseModel, UUID4, validator
from models import telegram
from models.telegram.base_types import ChatId


class MongoUserAuthStatus(str, Enum):
    pending = 'pending'
    success = 'success'


class MongoGitHubUser(BaseModel):
    user_id: int
    login: str
    name: str


class MongoUserAuthSuccess(BaseModel):
    token: str
    type: str
    github: MongoGitHubUser
    status: MongoUserAuthStatus = MongoUserAuthStatus.success

    class Config:
        use_enum_values = True


class MongoUserAuthPending(BaseModel):
    state: str
    message_id: Optional[str]
    status: MongoUserAuthStatus = MongoUserAuthStatus.pending

    class Config:
        use_enum_values = True


class MongoUserLang(BaseModel):
    current: str
    telegram: str


class MongoUserPrivacy(BaseModel):
    chat_id: ChatId


class MongoUserSettings(BaseModel):
    lang: MongoUserLang
    privacy: MongoUserPrivacy


class MongoUser(BaseModel):
    user_id: int
    settings: MongoUserSettings
    auth: Union[MongoUserAuthPending, MongoUserAuthSuccess]

    @staticmethod
    def new_from(user_id: int, chat_id: ChatId, lang: str):
        lang_settings = MongoUserLang(current=lang, telegram=lang)
        privacy_settings = MongoUserPrivacy(chat_id=chat_id)
        user_settings = MongoUserSettings(
            lang=lang_settings,
            privacy=privacy_settings
        )

        auth_status = MongoUserAuthPending(
            state=str(uuid.uuid4()),
            status=MongoUserAuthStatus.pending
        )

        return MongoUser(
            user_id=user_id,
            settings=user_settings,
            auth=auth_status
        )
