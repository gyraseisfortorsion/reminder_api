from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
class ChatBase(BaseModel):
    user_id: UUID
    title: Optional[str] = None

class ChatCreate(ChatBase):
    pass

class ChatUpdate(ChatBase):
    updated_at: datetime

class ChatRead(ChatBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode: True
