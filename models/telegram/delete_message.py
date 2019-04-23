from pydantic import BaseModel
from .base_types import ChatId


class DeleteMessage(BaseModel):
    chat_id: ChatId
    message_id: int
