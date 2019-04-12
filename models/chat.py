from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
from pydantic import BaseModel, validator
from models.base_types import ChatType, OptStr, OptBool, OptAny
# from models import message


class Chat(BaseModel):
    id: int
    type: ChatType
    title: OptStr
    username: OptStr
    first_name: OptStr
    last_name: OptStr
    all_members_are_administrators: OptBool
    photo: OptAny
    description: OptStr
    invite_link: OptStr
    pinned_message: Optional['Message']
    sticker_set_name: OptStr
    can_set_sticker_set: OptBool
