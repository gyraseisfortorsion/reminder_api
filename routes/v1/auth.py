from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core import get_db
from schemas import LoginForm, UserCreate, UserPreferencesUpdate, UserPreferencesRead, UserRead
from services import auth_service, user_service, user_preferences_service

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post("/login")
async def login(form: LoginForm, db: Session = Depends(get_db)):
    return await auth_service.login_for_access_token(form, db)

@router.post("/register")
def register(body: UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_email(body.email, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = user_service.create(db, body)
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
    return "User created successfully"

@router.put("/preferences", response_model = UserPreferencesRead)
def set_user_preferences(body: UserPreferencesUpdate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    user_preferences = user_preferences_service.get_by_user_id(user.id, db)
    return user_preferences_service.update_new(db, user_preferences, body)

@router.get("/preferences", response_model = UserPreferencesRead)
def get_user_preferences(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return user_preferences_service.get_by_user_id(user.id, db)

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    return auth_service.logout(refresh_token, db)

@router.get("/me", response_model = UserRead)
def get_me(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    return auth_service.get_current_user(credentials.credentials, db)