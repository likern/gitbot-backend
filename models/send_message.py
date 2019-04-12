from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
from pydantic import BaseModel, validator

ChatId = Union[int, str]


class SendMessage(BaseModel):
    chat_id: ChatId
    text: str
    parse_mode: Optional[str]
    disable_web_page_preview: Optional[bool]
    disable_notification: Optional[bool]
    reply_to_message_id: Optional[int]
    reply_markup: Optional[int]
