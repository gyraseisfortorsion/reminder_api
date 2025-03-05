from core import settings
import requests
from fastapi import HTTPException
# from .sip_client import sip_client
from models import Notification
from schemas import NotificationCreate, NotificationUpdate
from .base import ServiceBase
from sqlalchemy.orm import Session
from datetime import datetime
import requests
import logging

logger = logging.getLogger("Notifications")
class NotificationService(ServiceBase[Notification, NotificationCreate, NotificationUpdate]):

    def create_notification(self, type: str, reminder_id: str, task_id: str, db: Session):
        notification = Notification(type=type, reminder_id=reminder_id, task_id=task_id)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    def update_status(self, notification_id: str, status: str, db: Session):
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification.notification_status = status
        if status == "completed":
            notification.delivered_at = datetime.utcnow()
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

class CallService:
    def __init__(self):
        # self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        # self.AUDIO_DIR = "/shared_audio/audio"
        # self.SHARED_AUDIO_DIR = "/shared_audio"
        # self.audio_duration = 2
        pass


    # async def convert_text_to_audio(self, text: str, filename: str) -> str:
    #     """
    #     Use TTS (via OpenAI TTS streaming response) to generate an audio file.
    #     The file is saved to AUDIO_DIR with the given filename.
    #     Also estimates audio duration during streaming.
    #     """
    #     # Ensure directory exists before writing
    #     os.makedirs(self.AUDIO_DIR, exist_ok=True)
        
    #     file_path = os.path.join(self.AUDIO_DIR, filename)
    #     voice = "alloy"  # Adjust as needed

    #     # Variables to track byte count and estimate duration
    #     total_bytes = 0
    #     # Constants for MP3 estimation (approximate bit rate for OpenAI TTS)
    #     bit_rate = 32000  # 32 kbps, typical for speech audio

    #     # Write the TTS output to file
    #     with open(file_path, "wb") as speech_file:
    #         with self.openai_client.audio.speech.with_streaming_response.create(
    #             model="tts-1", input=text, voice=voice, speed=1
    #         ) as response:
    #             for chunk in response.iter_bytes():
    #                 speech_file.write(chunk)
    #                 total_bytes += len(chunk)
        
    #     # Estimate duration in seconds (total bits / bits per second)
    #     self.audio_duration = (total_bytes * 8) / bit_rate + 1
        
    #     logging.info(f"TTS file saved to {file_path}, estimated duration: {self.audio_duration:.2f}s")
    #     return file_path

    # async def convert_audio_to_asterisk_format(self, input_file: str) -> str:
    #     """
    #     Convert the TTS file to a WAV file with PCM 16-bit, mono, 8000Hz.
    #     Returns the path to the converted file.
    #     """
    #     base, _ = os.path.splitext(input_file)
    #     output_file = base + ".wav"
    #     cmd = ["sox", input_file, "-r", "8000", "-c", "1", "-b", "16", "-e", "signed-integer", output_file]
    #     logging.info(f"Converting audio: {' '.join(cmd)}")
    #     result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     if result.returncode != 0:
    #         raise Exception(f"Audio conversion failed: {result.stderr.decode()}")
    #     logging.info(f"Audio converted to {output_file}")
    #     return output_file
    
    def make_call(self, phone: str, message: str):
        try:
            # Using host.docker.internal to reach the calls service on the host network
            response = requests.get(
                f"{settings.CALLS_HOST}/call",
                params={
                    "phone_number": phone,
                    "message": message,
                    "token": settings.SECRET_KEY
                }
            )
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Call service error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Call service error: {str(e)}")

    


from core import settings
from ssl import create_default_context
from email.mime.text import MIMEText
from smtplib import SMTP

class EmailService():
    # def send_email_message(self, title:str, content: str, email: str):
    #     response = requests.post(
    #         "https://api.mailgun.net/v3/sandboxb8db567eb9d646ebaed2d47ecc1c77b0.mailgun.org/messages",
    #         auth=("api", settings.MAILGUN_API_KEY),
    #         data={"from": "Mailgun Sandbox <postmaster@sandboxb8db567eb9d646ebaed2d47ecc1c77b0.mailgun.org>",
    #         "to": email,
    #         "subject": title,
    #         "text": content})
    #     if response.json()["message"] == "Queued. Thank you.":
    #         return True
    #     return False




    def send_email_message(self, title: str, content: str, email: str):
        message = MIMEText(content, "html")
        message["From"] = settings.MAIL_USERNAME
        message["To"] = ",".join([email])
        message["Subject"] = title
        # print(message["From"], message["To"], message["Subject"])
        ctx = create_default_context()
        # print(HOST, PORT)
        try:
            with SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
                server.ehlo()
                server.starttls(context=ctx)
                # server.ehlo()
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                server.sendmail(message["From"], message["To"], message.as_string())
                server.quit()
            return True
        except Exception as e:
            logger.error(f"Email service error: {str(e)}")
            return False
    
call_service = CallService()
email_service = EmailService()
notification_service = NotificationService(Notification)