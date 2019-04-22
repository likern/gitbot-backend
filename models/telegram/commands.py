from enum import Enum
from typing import Any, Optional, Union
from pydantic import BaseModel, validator
from models.telegram.message import EntityTextMessage


class IssueAction(str, Enum):
    opened = 'opened'
    edited = 'edited'
    deleted = 'deleted'
    transferred = 'transferred'
    pinned = 'pinned'
    unpinned = 'unpinned'
    closed = 'closed'
    reopened = 'reopened'
    assigned = 'assigned'
    unassigned = 'unassigned'
    labeled = 'labeled'
    unlabeled = 'unlabeled'
    milestoned = 'milestoned'
    demilestoned = 'demilestoned'


class EntityStartCommand(EntityTextMessage):
    @validator('text')
    def check_text_field(cls, value):
        if not(value == '/start' or value.startswith('/start ')):
            raise ValueError(f'text field {value} should starts with /start')
        return value


class EntityDescriptionCommand(EntityTextMessage):
    @validator('text')
    def check_text_field(cls, value):
        if not(value == '/description' or value.startswith('/description ')):
            raise ValueError(
                f'text field {value} should starts with /description')
        return value
