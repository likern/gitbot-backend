from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
from pydantic import BaseModel, validator
from .base_types import OptAny
from .chat import Chat
from .user import User
from .message import EntityMessage, EntityTextMessage
from .commands import EntityStartCommand, EntityDescriptionCommand


class Update(BaseModel):
    update_id: int
    message: Optional[EntityMessage]
    edited_message: Optional[EntityMessage]
    channel_post: Optional[EntityMessage]
    edited_channel_post: Optional[EntityMessage]
    inline_query: OptAny
    chosen_inline_result: OptAny
    callback_query: OptAny
    shipping_query: OptAny
    pre_checkout_query: OptAny


class Message(Update):
    update_id: int
    message: EntityMessage
    edited_message: Optional[EntityMessage] = None
    channel_post: Optional[EntityMessage] = None
    edited_channel_post: Optional[EntityMessage] = None
    inline_query: OptAny = None
    chosen_inline_result: OptAny = None
    callback_query: OptAny = None
    shipping_query: OptAny = None
    pre_checkout_query: OptAny = None


class TextMessage(Message):
    message: EntityTextMessage


class StartCommand(Message):
    message: EntityStartCommand


class DescriptionCommand(Message):
    message: EntityDescriptionCommand
