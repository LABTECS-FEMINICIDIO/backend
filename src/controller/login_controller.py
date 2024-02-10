import os
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from src.database.database import engine
from src.model.models import UsuariosModels
import bcrypt


class LoginRequest(BaseModel):
    email: str
    senha: str


# FastAPI app
router = APIRouter()

# Secret key to sign JWT token
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# OAuth2PasswordBearer is a class to get the token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to create JWT token


def create_jwt_token(data: dict):
    to_encode = data.copy()
    to_encode["sub"] = str(to_encode.get("sub", ""))
    # Set expiration time for the token (e.g., 30 minutes)
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, os.getenv(
        "SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

# Function to get current user based on the token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"),
                             algorithm=os.getenv("ALGORITHM"))
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return email

# Route for user login


@router.post("/login")
async def login_for_access_token(login_data: LoginRequest):
    db = sessionmaker(bind=engine)
    db_session = db()

    user_db = db_session.query(UsuariosModels).filter_by(
        email=login_data.email).first()
    db_session.close()

    if user_db is None or not bcrypt.checkpw(login_data.senha.encode('utf-8'), user_db.senha.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    if user_db.acesso == False:
        raise HTTPException(
            status_code=401, detail="Você está sem permissão de acesso ao sistema.")

    token_data = {"sub": {"email": login_data.email, "perfil": user_db.perfil}}
    token = create_jwt_token(token_data)

    return {"access_token": token, "permission": user_db.perfil, "nome": user_db.nome, "id": user_db.id}
