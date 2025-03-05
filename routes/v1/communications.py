import os
import uuid
import time
import hashlib
import requests
from fastapi import FastAPI, HTTPException, Request, APIRouter, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response
from pydantic import BaseModel

from core import settings
from services import auth_service, email_service, call_service
from schemas import CallCreate, EmailCreate


router = APIRouter(prefix="/comms", tags=["Communications"])


@router.get("/call")
async def make_call(phone_number: str, message: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # check creds
    if not auth_service.get_role(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    call_service.make_call(phone_number, message)
    return {"message": "Success"}

@router.get("/send_email")
def send_email(email: str, title: str, message: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # check creds
    if not auth_service.get_role(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return email_service.send_email_message(title, message, email)
