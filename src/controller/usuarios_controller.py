from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from src.views.usuarios_views import (
    UsuarioViewr,
    Usuario,
    create_user,
    create_user_viewr,
    list_users,
    list_one_user,
    reset_user_password,
    update_user,
    delete_user
)

router = APIRouter()


class ListUsuario(BaseModel):
    id: Optional[UUID]
    nome: str
    email: str
    telefone: str
    senha: Optional[str] = None
    acesso: Optional[bool]
    perfil: Optional[str]


@router.post("/usuarios/")
async def create_user_controller(user: Usuario):
    try:
        return await create_user(user)
    except HTTPException as e:
        return e


@router.post("/usuarios/visualizador/")
async def create_user_controller(user: UsuarioViewr):
    try:
        return await create_user_viewr(user)
    except HTTPException as e:
        return e


@router.get("/usuarios/")
async def list_users_controller():
    return await list_users()


@router.get("/usuarios/{user_id}")
async def get_user_controller(user_id: UUID):
    try:
        return await list_one_user(user_id)
    except HTTPException as e:
        return e


@router.patch("/usuarios/{user_id}")
async def update_user_controller(user_id: UUID, user: dict):
    try:
        return await update_user(user_id, user)
    except HTTPException as e:
        return e


@router.delete("/usuarios/{user_id}")
async def delete_user_controller(user_id: UUID):
    try:
        return await delete_user(user_id)
    except HTTPException as e:
        return e


@router.post("/usuarios/reset/{user_id}")
async def reset_use_password_controller(user_id: UUID):
    try:
        return await reset_user_password(user_id)
    except HTTPException as e:
        return e
