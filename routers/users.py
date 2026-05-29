from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from .auth import get_current_user

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

router = APIRouter(
    prefix='/users',
    tags=['users']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PasswordChangeRequest(BaseModel):
    prevPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=1)

    model_config = {
        "json_schema_extra" : {
            "example" : {
                'prevPassword': '',
                'newPassword': ''
            }
        }
    }

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def fetch_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not authenticate user')
    result = db.query(Users).filter(Users.id == user.get('id')).first()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Did not find any info about user')
    
    return result

@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user: user_dependency,
                          db: db_dependency,
                          password_request: PasswordChangeRequest):
    if password_request.prevPassword == password_request.newPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='The previous password cannot be the same as the new password')

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not authenticate user')

    user_to_update = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found on data base')
    
    samePassword = bcrypt_context.verify(password_request.prevPassword, user_to_update.hashed_password)
    if not samePassword:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Password is incorrect')
    
    user_to_update.hashed_password = bcrypt_context.hash(password_request.newPassword)
    db.add(user_to_update)
    db.commit()
    
@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency,
                              db: db_dependency,
                              phone_number: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not authenticate user')
    
    user_to_update = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found on data base')
    
    user_to_update.phone_number = phone_number
    db.add(user_to_update)
    db.commit()
