"""
Celery worker main and celery_app for tasks sender.

Register all tasks from app/tasks
"""

from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import uuid

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core import settings
from models import Reminder
from schemas import ReminderCreate
from services import reminder_service, notification_service, call_service, email_service

# Configure Celery with Beat enabled.
app = Celery('celery_app', backend='redis://redis:6379/',
             broker='amqp://rabbitmq:5672/', timezone='Asia/Almaty')

# Set up the SQLAlchemy engine and session.
engine = create_engine(settings.DATABASE_URL, pool_size=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------------------------------------------
# Unified Periodic Task: Runs every 30 minutes for both recurrent and non-recurrent reminders
# ------------------------------------------------------------------
app.conf.beat_schedule = {
    'process_due_reminders_every_60_seconds': {
        'task': 'process_due_reminders',
        'schedule': timedelta(minutes=15), 
    },
}

@app.task(name="process_due_reminders")
def process_due_reminders():
    session = SessionLocal()
    try:
        now = datetime.utcnow()
        # Add 15 minutes to the current time to fetch upcoming reminders
        future_time = now + timedelta(minutes=15)
        due_reminders = session.query(Reminder).filter(
            Reminder.reminder_at <= future_time,
            Reminder.is_active == True,
            Reminder.reminder_status == 'pending'
        ).all()

        for reminder in due_reminders:
            for channel in reminder.channels:
                # Pass reminder.id instead of the entire object.
                send_notification_task.delay(reminder.id, channel)
                reminder.reminder_status = 'partially_done'
            
            if reminder.recurrence and reminder.recurrence.strip() != "":
                reminder.reminder_status = 'pending'
                recurrence = reminder.recurrence
                recurrence_days = None
                try:
                    recurrence_days = int(recurrence)
                except ValueError:
                    mapping = {
                        'week': 7,
                        '2 weeks': 14,
                        'month': 30,
                        '3 months': 90,
                        '6 months': 180,
                        'year': 365
                    }
                    recurrence_days = mapping.get(recurrence)
                if recurrence_days:
                    reminder.reminder_at = reminder.reminder_at + timedelta(days=recurrence_days)
            else:
                reminder.reminder_status = 'done'
            session.add(reminder)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ------------------------------------------------------------------
# Send Notification Task with Retry Logic
# ------------------------------------------------------------------
@app.task(bind=True, max_retries=3, name="send_notification_task")
def send_notification_task(self, reminder_id, channel):
    session = SessionLocal()
    res = None
    try:
        # Retrieve the reminder object by its ID.
        reminder = session.query(Reminder).get(reminder_id)
        if not reminder:
            return

        # Create a notification record in the database.
        notification = notification_service.create_notification(
            type=channel,
            reminder_id=reminder.id,
            task_id=self.request.id,
            db=session
        )
        if channel == "phone":
            phone = reminder.user.phone_number if not reminder.custom_phone else reminder.custom_phone
            if not phone:
                raise ValueError("Phone number is not provided")
            content = reminder.description
            res = call_service.make_call(phone, content)
            if not res:
                raise Exception("Phone call failed")
            notification_service.update_status(notification.id, "completed", session)
        elif channel == "email":
            email = reminder.user.email if not reminder.custom_email else reminder.custom_email
            if not email:
                raise ValueError("Email is not provided")
            title = reminder.title
            content = reminder.description
            res = email_service.send_email_message(title, content, email)
            if not res:
                raise Exception("Email sending failed")
            notification_service.update_status(notification.id, "completed", session)

    except Exception as exc:
        # Retry after 10 minutes (600 seconds)
        reminder.reminder_status = 'pending'
        session.add(reminder)
        raise self.retry(exc=exc, countdown=5 * 60)
    finally:
        session.close()
        return res



