from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core import get_db
from schemas import ReminderCreate, ReminderUpdate, ReminderRead
from services import auth_service, reminder_service

router = APIRouter(prefix="/reminders", tags=["Reminders"])

@router.post("/", response_model=ReminderRead)
def create_reminder(body: ReminderCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # check credentials
    if not auth_service.get_role(credentials.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return reminder_service.create(db, body)

@router.get("/{reminder_id}", response_model=ReminderRead)
def get_reminder(reminder_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # check credentials
    if not auth_service.get_role(credentials.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return reminder_service.get(db, reminder_id)

@router.get("/", response_model=list[ReminderRead])
def get_reminders(skip: int, limit: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # check credentials
    if not auth_service.get_role(credentials.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return reminder_service.get_multi(db, skip, limit)

@router.get("/user/", response_model=list[ReminderRead])
def get_user_reminders(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    # check credentials
    if not auth_service.get_role(credentials.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user.reminders

@router.put("/{reminder_id}", response_model=ReminderRead)
def update_reminder(reminder_id: str, body: ReminderUpdate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # check credentials
    user = auth_service.get_current_user(credentials.credentials, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    reminder = reminder_service.get(db, reminder_id)
    if reminder.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return reminder_service.update(db, reminder, body)

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    # check credentials
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    reminder = reminder_service.get(db, reminder_id)
    if reminder.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    reminder_service.delete(db, reminder_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)