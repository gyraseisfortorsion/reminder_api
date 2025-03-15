from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

class UserBase(BaseModel):
    name: str
    surname: str
    password_hash: str
    email: str
    phone_number: str
    last_signed_at: Optional[datetime]
    avatar_url: Optional[str]
    is_active: Optional[bool]
    is_verified: Optional[bool]
    is_blocked: Optional[bool]

class UserCreate(BaseModel):
    name: str
    surname: str
    password_hash: str
    email: EmailStr
    phone_number: str

class UserUpdate(BaseModel):
    name: str
    surname: str
    email: str
    phone_number: str



class UserPreferencesBase(BaseModel):
    user_id: uuid.UUID
    timezone: Optional[str]
    language: Optional[str]
    is_whatsapp_enabled: bool
    is_telegram_enabled: bool
    is_email_enabled: bool
    is_sms_enabled: bool
    is_phone_enabled: bool
    need_confirmation: bool
    class Config:
        orm_mode = True

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesUpdate(BaseModel):
    timezone: str
    language: str
    is_whatsapp_enabled: bool
    is_telegram_enabled: bool
    is_email_enabled: bool
    is_sms_enabled: bool
    is_phone_enabled: bool
    need_confirmation: bool
    updated_at: datetime

class UserPreferencesRead(UserPreferencesBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    preferences_set: bool
    class Config:
        orm_mode = True

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    # user_preferences: Optional[UserPreferencesRead] = None
    class Config:
        orm_mode = True

class LoginForm(BaseModel):
    email: EmailStr
    password: str
