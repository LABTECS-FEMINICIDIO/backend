from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg2 import IntegrityError
from sqlalchemy.orm import sessionmaker
from src.database.database import engine
from src.model.models import UsuariosModels
from typing import List, Optional
import uuid
from pydantic import BaseModel
import bcrypt
from uuid import UUID
from datetime import datetime, timedelta


class Usuario(BaseModel):
    nome: str
    email: str
    telefone: str
    senha: Optional[str] = None
    perfil: Optional[str] = "pesquisador"


class UsuarioViewr(BaseModel):
    nome: str
    email: str
    telefone: str
    senha: Optional[str] = None
    acesso: Optional[bool] = True
    perfil: str = "visualizador"


class ListUsuario(BaseModel):
    id: Optional[UUID]
    nome: str
    email: str
    telefone: str
    senha: Optional[str] = None
    acesso: Optional[bool] = None


async def create_user_viewr(user: UsuarioViewr):
    if user_exists(user.email):
        raise HTTPException(
            status_code=409, detail=f"O usuário {user.email} já está cadastrado."
        )

    default_password = f"{user.nome[:3]}{user.telefone[:3]}"

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), salt)
    decoded_password = hashed_password.decode('utf-8')

    db_user = UsuariosModels(
        nome=user.nome,
        email=user.email,
        telefone=user.telefone,
        senha=decoded_password,
        acesso=True,
        perfil="visualizador"
    )

    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    try:
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=409, detail=f"O usuário {user.email} já está cadastrado."
        )
    finally:
        db_session.close()

    return user


async def create_user(user: Usuario):
    if user_exists(user.email):
        raise HTTPException(
            status_code=409, detail=f"O usuário {user.email} já está cadastrado."
        )

    default_password = f"{user.nome[:3]}{user.telefone[:3]}"

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), salt)
    decoded_password = hashed_password.decode('utf-8')

    db_user = UsuariosModels(
        nome=user.nome,
        email=user.email,
        telefone=user.telefone,
        senha=decoded_password,
        acesso=False,
        perfil=user.perfil
    )

    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    try:
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=409, detail=f"O usuário {user.email} já está cadastrado."
        )
    finally:
        db_session.close()

    return user


async def list_users():
    db = sessionmaker(bind=engine)
    db_session = db()
    users = db_session.query(UsuariosModels).all()
    db_session.close()
    return users

async def list_one_user(user_id: uuid.UUID):
    db = sessionmaker(bind=engine)
    db_session = db()

    user_db = db_session.query(UsuariosModels).filter(
        UsuariosModels.id == user_id).first()

    db_session.close()

    if user_db is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user = jsonable_encoder(user_db)

    return user


async def update_user(user_id: uuid.UUID, user: dict):
    db = sessionmaker(bind=engine)
    db_session = db()

    db_user = db_session.query(UsuariosModels).filter(
        UsuariosModels.id == user_id).first()

    if db_user is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    for key, value in user.items():
        if key == "senha":
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(value.encode('utf-8'), salt)
            decoded_password = hashed_password.decode('utf-8')
            setattr(db_user, key, decoded_password)
        else:
            setattr(db_user, key, value)

    db_session.commit()

    db_session.refresh(db_user)

    db_session.close()

    updated_user = jsonable_encoder(db_user)

    return updated_user


async def reset_user_password(user_id: uuid.UUID):
    db = sessionmaker(bind=engine)
    db_session = db()

    try:
        db_user = db_session.query(UsuariosModels).filter(
            UsuariosModels.id == user_id).first()

        if db_user is None:
            raise HTTPException(
                status_code=404, detail="Usuário não encontrado")

        default_password = f"{db_user.nome[:3]}{db_user.telefone[:3]}"

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), salt)
        decoded_password = hashed_password.decode('utf-8')

        db_user.senha = decoded_password

        db_session.commit()
        db_session.refresh(db_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db_session.close()

    return {
        "message": "Senha resetada com sucesso!"
    }


async def delete_user(user_id: uuid.UUID):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_user = db_session.query(UsuariosModels).filter(
        UsuariosModels.id == user_id).first()
    if db_user is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db_session.delete(db_user)
    db_session.commit()
    db_session.close()
    return db_user


def user_exists(email: str) -> bool:
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    existing_user = db_session.query(
        UsuariosModels).filter_by(email=email).first()

    db_session.close()

    return existing_user is not None


def update_recovery_code(email, recovery_code):
    db = sessionmaker(bind=engine)
    db_session = db()
    user = db_session.query(UsuariosModels).filter(UsuariosModels.email == email).first()
    
    if user is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user.recovery_code = recovery_code
    user.recovery_code_created_at = datetime.utcnow()
    db_session.commit()

def clear_recovery_code(email):
    db = sessionmaker(bind=engine)
    db_session = db()
    user = db_session.query(UsuariosModels).filter(UsuariosModels.email == email).first()
    if user:
        user.recovery_code = None
        user.recovery_code_created_at = None
        db_session.commit()

def is_recovery_code_valid(user):
    if user.recovery_code_created_at:
        return datetime.utcnow() - user.recovery_code_created_at < timedelta(minutes=30)
    return False

def change_password_with_recovery_code(email: str, recovery_code: str, new_password: str):
    db = sessionmaker(bind=engine)
    db_session = db()

    user = db_session.query(UsuariosModels).filter(UsuariosModels.email == email).first()
    if user:
        print("ta valendo???", is_recovery_code_valid(user))
        print("codigo do user", user.recovery_code)
        print("codigo enviado", recovery_code)
        if is_recovery_code_valid(user) or user.recovery_code != recovery_code:
            raise HTTPException(status_code=400, detail="Código de recuperação inválido ou expirado.")
        
        if user.recovery_code == recovery_code and is_recovery_code_valid(user):
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            decoded_password = hashed_password.decode('utf-8')

            user.senha = decoded_password

            clear_recovery_code(db_session, email)
            db_session.commit()

            return {"message": "Senha alterada com sucesso."}
    else:
        raise HTTPException(status_code=404, detail="E-mail não encontrado")
