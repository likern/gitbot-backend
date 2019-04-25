from enum import Enum
from typing import Any, Optional, Union
from pydantic import BaseModel


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


class IssueEvent(BaseModel):
    action: IssueAction
    issue: Any
    changes: Optional[Any]
    changes: Optional[Any]
    assignee: Optional[Any]
    label: Optional[Any]


class IssueOpened(IssueEvent):
    action: IssueAction = IssueAction.opened


class IssueEdited(IssueEvent):
    action: IssueAction = IssueAction.opened


class IssueClosed(IssueEvent):
    action: IssueAction = IssueAction.closed
