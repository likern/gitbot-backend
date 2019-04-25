from enum import Enum
from typing import Any, Optional, Union, List
from pydantic import BaseModel
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


class InstallationCreated(BaseModel):
    action: InstallationAction = InstallationAction.created
    installation: InstallationItem
    repositories: List[Repository]
    sender: Sender

    class Config:
        use_enum_values = True


class InstallationDeleted(BaseModel):
    action: InstallationAction = InstallationAction.deleted
    installation: InstallationItem
    repositories: List[Repository]
    sender: Sender

    class Config:
        use_enum_values = True


class InstallationNewPermissions(BaseModel):
    action: InstallationAction = InstallationAction.new_permissions_accepted
    installation: InstallationItem
    repositories: List[Repository]
    sender: Sender

    class Config:
        use_enum_values = True
