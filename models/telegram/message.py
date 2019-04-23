from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
from pydantic import BaseModel, validator
from models.telegram.chat import Chat
from models.telegram.user import User


class EntityMessage(BaseModel):
    message_id: int
    user: Optional[User]
    date: int
    chat: Chat
    forward_from: Optional[Any]
    forward_from_chat: Optional[Any]
    forward_from_message_id: Optional[int]
    forward_signature: Optional[str]
    forward_date: Optional[int]
    reply_to_message: Optional[Any]
    edit_date: Optional[int]
    media_group_id: Optional[str]
    author_signature: Optional[str]
    text: Optional[str]
    entities: Optional[Any]
    caption_entities: Optional[Any]
    audio: Optional[Any]
    document: Optional[Any]
    animation: Optional[Any]
    game: Optional[Any]
    photo: Optional[Any]
    sticker: Optional[Any]
    video: Optional[Any]
    voice: Optional[Any]
    video_note: Optional[Any]
    caption: Optional[str]
    contact: Optional[Any]
    location: Optional[Any]
    venue: Optional[Any]
    new_chat_members: Optional[Any]
    left_chat_member: Optional[Any]
    new_chat_title: Optional[str]
    new_chat_photo: Optional[Any]
    delete_chat_photo: Optional[bool]
    group_chat_created: Optional[bool]
    supergroup_chat_created: Optional[bool]
    channel_chat_created: Optional[bool]
    migrate_to_chat_id: Optional[int]
    migrate_from_chat_id: Optional[int]
    pinned_message: Optional[Any]
    invoice: Optional[Any]
    successful_payment: Optional[Any]
    connected_website: Optional[str]
    passport_data: Optional[Any]

    class Config:
        fields = {
            'user': 'from'
        }


class EntityTextMessage(EntityMessage):
    text: str

    @validator('text')
    def check_text_length(cls, value):
        length = len(value)
        if length > 4096:
            raise ValueError(f'text length {length} is too large')
        return value
