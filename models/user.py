from pydantic import BaseModel
from models.base_types import ChatType, OptStr, OptBool, OptAny


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: OptStr
    username: OptStr
    language_code: OptStr
