from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
from pydantic import BaseModel, validator
from models.base_types import OptAny
from models.chat import Chat
from models.user import User
from models.message import Message


class Update(BaseModel):
    update_id: int
    message: Optional[Message]
    edited_message: Optional[Message]
    channel_post: Optional[Message]
    edited_channel_post: Optional[Message]
    inline_query: OptAny
    chosen_inline_result: OptAny
    callback_query: OptAny
    shipping_query: OptAny
    pre_checkout_query: OptAny
