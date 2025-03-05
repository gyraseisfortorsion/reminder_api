from sqlalchemy.orm import relationship
from .base import Model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

class User(Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'reminder'}

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    last_signed_at = Column(DateTime)
    avatar_url = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    role = Column(Enum('admin', 'user', name='roles_reminder'), default='user')

    user_preferences = relationship('UserPreferences', back_populates='user')
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    reminders = relationship('Reminder', back_populates='user')
    chats = relationship('Chat', back_populates='user')
    messages = relationship('Message', back_populates='user')

class UserPreferences(Model):
    __tablename__ = 'user_preferences'
    __table_args__ = {'schema': 'reminder'}

    user_id = Column(UUID, ForeignKey('reminder.users.id'))
    timezone = Column(String)
    language = Column(String)
    is_whatsapp_enabled = Column(Boolean, default=False)
    is_telegram_enabled = Column(Boolean, default=False)
    is_email_enabled = Column(Boolean, default=False)
    is_sms_enabled = Column(Boolean, default=False)
    is_phone_enabled = Column(Boolean, default=False)
    need_confirmation = Column(Boolean, default=False)
    preferences_set = Column(Boolean, default=False, nullable=False)

    user = relationship('User', back_populates='user_preferences')

class RefreshToken(Model):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'schema': 'reminder'}

    user_id = Column(UUID, ForeignKey("reminder.users.id"))
    refresh_token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

class Reminder(Model):
    __tablename__ = 'reminders'
    __table_args__ = {'schema': 'reminder'}

    user_id = Column(UUID, ForeignKey('reminder.users.id'))
    title = Column(String, nullable=False)
    description = Column(String)
    recurrence = Column(String) # needs validator since both words and numbers can be here
    reminder_at = Column(TIMESTAMP(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    channels = Column(ARRAY(Enum('email', 'sms', 'whatsapp', 'telegram', 'phone', name='channels')), nullable=False)
    reminder_status = Column(Enum('done', 'partially_done', 'pending', name='reminder_status'), default='pending')
    custom_phone = Column(String)
    custom_email = Column(String)

    user = relationship('User', back_populates='reminders')
    notifications = relationship('Notification', back_populates='reminder')
    message = relationship('Message', back_populates='reminder')

class Notification(Model):
    __tablename__ = 'notifications'
    __table_args__ = {'schema': 'reminder'}

    reminder_id = Column(UUID, ForeignKey('reminder.reminders.id'))
    type = Column(Enum('email', 'sms', 'whatsapp', 'telegram', 'phone', name='channels'), nullable=False)
    notification_status = Column(Enum('pending', 'completed', 'missed', 'cancelled', name='notification_status'), default='pending')
    delivered_at = Column(DateTime)
    task_id = Column(UUID, nullable=False)

    reminder = relationship('Reminder', back_populates='notifications')

class Chat(Model):
    __tablename__ = 'chats'
    __table_args__ = {'schema': 'reminder'}

    user_id = Column(UUID, ForeignKey('reminder.users.id'), nullable=False)
    title = Column(String, nullable=True)

    user = relationship('User', back_populates='chats')
    messages = relationship('Message', back_populates='chat')

class Message(Model):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'reminder'}

    chat_id = Column(UUID, ForeignKey('reminder.chats.id'))
    user_id = Column(UUID, ForeignKey('reminder.users.id'))
    message = Column(String, nullable=False)
    is_llm = Column(Boolean, default=False, nullable=False)
    reminder_id = Column(UUID, ForeignKey('reminder.reminders.id'))

    chat = relationship('Chat', back_populates='messages')
    reminder = relationship('Reminder', back_populates='message')
    user = relationship('User', back_populates='messages')