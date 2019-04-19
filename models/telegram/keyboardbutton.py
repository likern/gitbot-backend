from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
from pydantic import BaseModel, validator
from models.telegram.chat import Chat
from models.telegram.user import User
from models.telegram.base_types import OptStr, OptBool, OptAny


class InlineKeyboardButton(BaseModel):
    text: str
    url: OptStr
    callback_data: OptStr
    switch_inline_query: OptStr
    switch_inline_query_current_chat: OptStr
    callback_game: OptAny
    pay: OptBool


class InlineUrlButton(InlineKeyboardButton):
    url: str
    callback_data: OptStr = None
    switch_inline_query: OptStr = None
    switch_inline_query_current_chat: OptStr = None
    callback_game: OptAny = None
    pay: OptBool = None


class InlineCallbackButton(InlineKeyboardButton):
    callback_data: str
    url: OptStr = None
    switch_inline_query: OptStr = None
    switch_inline_query_current_chat: OptStr = None
    callback_game: OptAny = None
    pay: OptBool = None


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: List[List[InlineKeyboardButton]]
