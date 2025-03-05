from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class MessageBase(BaseModel):
    chat_id: UUID
    message: str
    is_llm: bool
    reminder_id: Optional[UUID]

class MessageCreate(MessageBase):
    pass

class MessageUpdate(MessageBase):
    updated_at: datetime

class MessageRead(MessageBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        orm_mode: True

