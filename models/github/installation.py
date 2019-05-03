from enum import Enum
from typing import Any, Optional, Union, List
from pydantic import BaseModel, validator
from .account import Account
from .repository import Repository
from .sender import Sender


class InstallationAction(str, Enum):
    created = 'created'
    deleted = 'deleted'
    new_permissions_accepted = 'new_permissions_accepted'


class InstallationItem(BaseModel):
    access_tokens_url: str
    account: Account
    app_id: int
    created_at: int
    events: List[str]
    html_url: str
    id: int
    permissions: Any
    repositories_url: str
    repository_selection: str
    single_file_name: Optional[Any]
    target_id: int
    target_type: str
    updated_at: str


class InstallationEvent(BaseModel):
    action: InstallationAction
    installation: InstallationItem
    repositories: List[Repository]
    sender: Sender


class InstallationCreated(InstallationEvent):
    installation: InstallationItem
    repositories: List[Repository]
    sender: Sender

    @validator('action')
    def check_type(cls, value):
        if value != InstallationAction.created:
            raise ValueError('Not InstallationCreated')
        return value

    class Config:
        use_enum_values = True


class InstallationDeleted(InstallationEvent):
    installation: InstallationItem
    repositories: List[Repository]
    sender: Sender

    @validator('action')
    def check_type(cls, value):
        if value != InstallationAction.deleted:
            raise ValueError('Not InstallationDeleted')
        return value

    class Config:
        use_enum_values = True


class InstallationNewPermissions(InstallationEvent):
    installation: InstallationItem
    repositories: List[Repository]
    sender: Sender

    @validator('action')
    def check_type(cls, value):
        if value != InstallationAction.new_permissions_accepted:
            raise ValueError('Not InstallationNewPermissions')
        return value

    class Config:
        use_enum_values = True
