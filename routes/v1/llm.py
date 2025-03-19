from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from schemas import LLMQuery
from core import get_db
from services import auth_service, llm_service

router = APIRouter(prefix="/llm", tags=["LLM"])

@router.post("/")
def create_reminder(message: LLMQuery, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return llm_service.query_llm_openai(message.message, user, db)