from enum import Enum
from typing import Any, Optional, Union

OptStr = Optional[str]
OptInt = Optional[int]
OptBool = Optional[bool]
OptAny = Optional[Any]

ChatId = Union[int, str]


class ChatType(str, Enum):
    private = 'private'
    group = 'group'
    supergroup = 'supergroup'
    channel = 'channel'
