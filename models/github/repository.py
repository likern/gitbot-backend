from pydantic import BaseModel


class Repository(BaseModel):
    full_name: str
    id: int
    name: str
    node_id: str
    private: bool
