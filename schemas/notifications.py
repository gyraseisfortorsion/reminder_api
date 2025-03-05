from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class ChannelEnum(str, Enum):
    email = 'email'
    sms = 'sms'
    whatsapp = 'whatsapp'
    telegram = 'telegram'
    phone = 'phone'

class NotificationStatusEnum(str, Enum):
    pending = 'pending'
    completed = 'completed'
    missed = 'missed'
    cancelled = 'cancelled'

class NotificationBase(BaseModel):
    reminder_id: UUID
    type: ChannelEnum
    notification_status: NotificationStatusEnum = NotificationStatusEnum.pending
    delivered_at: Optional[datetime] = None
    task_id: UUID

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(NotificationBase):
    updated_at: datetime

class NotificationRead(NotificationBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        orm_mode = True

class CallCreate(BaseModel):
    phone_number: str = Field(..., example="1234567890")
    message: str = Field(..., example="Hello, this is a reminder")

class EmailCreate(BaseModel):
    title: str = Field(..., example="Reminder")
    message: str = Field(..., example="Hello, this is a reminder")
    email: str = Field(..., example="test@mail.com")