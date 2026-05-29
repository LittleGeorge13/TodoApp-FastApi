from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Request
from pydantic import BaseModel
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
from config import settings

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

#Classes
class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "test@email.com",
                "username": "Squiky",
                "first_name": "Jorge",
                "last_name": "Esqueda",
                "password": "SecretPassWord",
                "role": "Developer",
                "phone_number": "4491231234"
            }
        }
    }

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependencies
db_dependency = Annotated[Session, Depends(get_db)]
login_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]

templates = Jinja2Templates(directory='templates')

# Non api methods
def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first();
    if not user:
        return None
    
    if bcrypt_context.verify(password, user.hashed_password):
        return user
    return None

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = { "sub": username, "id": user_id, 'role': role }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
                                , detail='Could not validate user')
        return { 'username': username, 'id' : user_id, 'user_role': user_role }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
                                , detail='Could not validate user')

# Pages
@router.get('/login-page')
def render_login_page(request: Request):
    return templates.TemplateResponse(name="login.html", request= request)

@router.get('/register-page')
def render_register_page(request: Request):
    return templates.TemplateResponse(name="register.html", request= request)

# Api methods
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.role,
        is_active = True,
        phone_number = create_user_request.phone_number
    )

    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: login_dependency, db: db_dependency):
    valid_user = authenticate_user(username= form_data.username,password= form_data.password,db= db)

    if valid_user:
        token = create_access_token(valid_user.username, valid_user.id, valid_user.role, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        return { 'access_token': token, "token_type": 'bearer' }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
                                , detail='Could not validate User')