from datetime import datetime
from sqlalchemy.orm import Session
from models import User, UserPreferences, RefreshToken
from .base import ServiceBase
from schemas import UserCreate, UserUpdate, UserPreferencesCreate, UserPreferencesUpdate
from utils import hash_password
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

class UserService(ServiceBase[User, UserCreate, UserUpdate]):
    def get_user_by_email(self, email: str, db: Session) -> User:
        return db.query(User).filter(User.email == email).first()
    
    def create(self, db, obj_in, model = None):
        obj_in.password_hash = hash_password(obj_in.password_hash)
        
        user = super().create(db, obj_in, model)
        user_preferences_dict = {
            "user_id": user.id,
        }
        user_preferences = UserPreferences(**user_preferences_dict)
        db.add(user_preferences)
        db.flush()
        return user
    
class UserPrefencesService(ServiceBase[UserPreferences, UserPreferencesCreate, UserPreferencesUpdate]):
    def get_by_user_id(self, id, db: Session):
        user_prefs = db.query(UserPreferences).filter(UserPreferences.user_id == id).first()

        if not user_prefs:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="This user does not have preferences")
        return user_prefs
    
    def update_new(self, db: Session, db_obj, obj_in):
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db_obj.preferences_set = True
        db.add(db_obj)
        db.flush()
        return db_obj
    



user_service = UserService(User)
user_preferences_service = UserPrefencesService(UserPreferences)