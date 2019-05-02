from enum import Enum
from typing import Any, Optional, Union, List
from pydantic import BaseModel

class IssueState(str, Enum):
    open = 'open'
    closed = 'closed'


class IssueEdit(BaseModel):
    state: IssueState
    title: str
    body: str
    milestone: int
    labels: List[str]
    assignees: List[str]

class IssueClose(BaseModel):
    state: IssueState = IssueState.closed

    class Config:
        use_enum_values = True

class IssueOpen(BaseModel):
    state: IssueState = IssueState.open

    class Config:
        use_enum_values = True