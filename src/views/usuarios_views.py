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

        db_user.password = decoded_password

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
