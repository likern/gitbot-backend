from enum import Enum
from typing import Any, Optional, Union
from pydantic import BaseModel, validator
from models.telegram.message import TextMessage


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


class StartCommand(TextMessage):
    @validator('text')
    def check_text_field(cls, value):
        if not(value == '/start' or value.startswith('/start ')):
            raise ValueError(f'text field {value} should starts with /start')
        return value
