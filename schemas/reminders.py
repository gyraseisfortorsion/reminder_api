from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import uuid
from typing import List
from enum import Enum
class ChannelsEnum(str, Enum):
    whatsapp = 'whatsapp'
    telegram = 'telegram'
    email = 'email'
    sms = 'sms'
    phone = 'phone'

class ReminderStatusEnum(str, Enum):
    done = 'done'
    partially_done = 'partially_done'
    pending = 'pending'
class NotificationStatusEnum(str, Enum):
    pending = 'pending'
    completed = 'completed'
    missed = 'missed'
    cancelled = 'cancelled'

class ReminderBase(BaseModel):
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    recurrence: Optional[str]
    reminder_at: datetime
    is_active: Optional[bool] = True
    channels: List[ChannelsEnum]
    reminder_status: Optional[ReminderStatusEnum] = ReminderStatusEnum.pending
    custom_phone: Optional[str] = None
    custom_email: Optional[str] = None

    @validator('recurrence')
    def validate_recurrence(cls, v):
        valid_values = ['week', '2 weeks', 'month', '3 months', '6 months', 'year', '']
        try:
            if v:
                int(v)
            else:
                return v
        except ValueError:
            if v not in valid_values:
                raise ValueError(f"recurrence must be an integer or one of {valid_values}")
        return v

class ReminderCreate(ReminderBase):
    custom_phone: Optional[str] = None
    custom_email: Optional[str] = None

class ReminderUpdate(ReminderBase):
    custom_phone_number: Optional[str] = None
    custom_email: Optional[str] = None
    updated_at: datetime

class ReminderRead(ReminderBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        orm_mode = True

class LLMQuery(BaseModel):
    message: str