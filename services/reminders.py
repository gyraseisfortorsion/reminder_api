from datetime import datetime
from sqlalchemy.orm import Session
from models import Reminder, User
from .base import ServiceBase
from schemas import ReminderCreate, ReminderUpdate
import google.generativeai as genai
from core import settings
from typing import Optional, List
import uuid
from schemas import ChannelEnum
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .notifications import email_service, call_service
import pytz
import logging

logger = logging.getLogger("Reminders")

class ReminderService(ServiceBase[Reminder, ReminderCreate, ReminderUpdate]):
    # TODO: delegate notifications to separate celery tasks; handle recurrence
    async def send_notification(self, reminder: Reminder):
        """
        Send a notification to the user based on the user's preferences.
        """
        # Get the user's preferences.
        user_preferences = reminder.user.user_preferences
        if not user_preferences:
            raise ValueError("User preferences not found")
        if user_preferences.is_whatsapp_enabled and reminder.whatsapp_status == 'pending':
            # Send a WhatsApp message.
            pass
        if user_preferences.is_telegram_enabled and reminder.telegram_status == 'pending':
            # Send a Telegram message.
            phone = reminder.user.phone_number if not reminder.custom_phone else reminder.custom_phone
            if not phone:
                raise ValueError("No phone provided")
            if not call_service.make_call(reminder.user.phone_number, reminder.description):
                reminder.reminder_status = "partially_done"
            reminder.reminder_status = "done"
        if user_preferences.is_email_enabled and reminder.email_status == 'pending':
            # Send an email.
            email = reminder.user.email if not reminder.custom_email else reminder.custom_email
            if not email:
                reminder.reminder_status = "partially_done"
                raise ValueError("No email provided")
            if not email_service.send_email_message(reminder.title, reminder.description, reminder.user.email):
                reminder.reminder_status = "partially_done"
                # TODO: this will always be returned as done, fix this
            reminder.reminder_status = "done"
        if user_preferences.is_sms_enabled and reminder.sms_status == 'pending':
            # Send an SMS.
            pass
        if user_preferences.is_phone_enabled and reminder.phone_status == 'pending':
            # Make a phone call.
            pass
        
        return reminder
    
    def create_from_llm(self, user_id: str, title: str, description: Optional[str],
                         reminder_at: str, channels: List[str], recurrence: Optional[str] = None,
                        custom_phone: Optional[str] = None, custom_email: Optional[str] = None, is_certain_time: Optional[bool] = False):
        """
        Create a reminder from LLM input. IF THE USER MESSAGE IS A SIMPLE GREETING OR GENERAL QUERY, RESPOND DIRECTLY WITHOUT CALLING ANY REMINDER CREATION FUNCTIONS.
        Args:
            - user_id: str (provided in the prompt)
            - title: str (what the reminder is about)
            - description: str you should decide what would be the description on your own, based on the title or user provided details
            - reminder_at: str (ISO formatted datetime string), should be provided in the format of isoformat
            - channels: List[str] (notification methods: e.g. "whatsapp", "phone", "sms", "email")
            - recurrence: Optional[str] (how often the reminder should repeat), should be set to 1 if it doesn't repeat
            - custom_phone: Optional[str]
            - custom_email: Optional[str]
            - is_certain_time: Optional[bool] (whether the provided time is certain (e.g. "tomorrow at 9am") or relative (e.g. "in 2 hours"), if relative then False)
        """

        engine = create_engine(settings.DATABASE_URL, pool_size=20)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
        db = SessionLocal()
        # Convert reminder_at from string to datetime
        # get user timezone
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        if not user:
            raise ValueError("User not found")
        user_timezone = user.user_preferences[0].timezone
        if not user_timezone:
            raise ValueError("User timezone not found")
        
         # Convert reminder_at from string to datetime.
        reminder_at_dt = datetime.fromisoformat(reminder_at)
        # If the datetime is naive, assume it's in UTC.
        if reminder_at_dt.tzinfo is None:
            reminder_at_dt = pytz.utc.localize(reminder_at_dt)
        
        # Convert the time to the user's timezone using pytz.
        user_tz = pytz.timezone(user_timezone)
        print(f"User timezone: {user_tz}")
        logger.info(f"User timezone: {user_tz}")

        if is_certain_time:
            # If is_certain_time is True, treat the time as already in the user's timezone
            # Strip timezone info and apply user's timezone without changing the time values
            naive_time = reminder_at_dt.replace(tzinfo=None)
            reminder_at_dt = user_tz.localize(naive_time)
        else:
            # Convert from current timezone to the user's timezone
            reminder_at_dt = reminder_at_dt.astimezone(user_tz)

        print(f"Reminder at: {reminder_at_dt}")
        logger.info(f"Reminder at: {reminder_at_dt}")
        # reminder_at_dt = datetime.fromisoformat(reminder_at)
        # Convert channels strings to ChannelEnum values manually
        channels_enum = [ChannelEnum(item) for item in channels]
        
        reminder_data = {
            "user_id": uuid.UUID(user_id),
            "title": title,
            "description": description,
            "recurrence": recurrence,
            "reminder_at": reminder_at_dt,
            "channels": channels_enum,
            "custom_phone": custom_phone,
            "custom_email": custom_email
        }
        reminder = Reminder(**reminder_data)
        reminder = self.create_from_object(db, reminder)
        return str({
            "id": str(reminder.id),
            "user_id": str(reminder.user_id),
            "title": reminder.title,
            "description": reminder.description,
            "recurrence": reminder.recurrence if reminder.recurrence and reminder.recurrence!="" else None,
            "reminder_at": reminder.reminder_at.isoformat(),
            "channels": [channel for channel in reminder.channels],
            "custom_phone": reminder.custom_phone,
            "custom_email": reminder.custom_email
        })
    
    def create_from_object(self, db, reminder: Reminder):
        """
        Create a new reminder.
        """
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    def delete(self, db: Session, id: str):
        reminder = self.get(db, id)
        # find all messages and notifications which reference this reminder and set their remider_id to null
        for notification in reminder.notifications:
            db.delete(notification)
        for message in reminder.message:
            message.reminder_id = None
            db.add(message)
        db.delete(reminder)
        db.commit()
        return reminder


reminder_service = ReminderService(Reminder)