from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from src.views.usuarios_views import (
    create_user,
    list_users,
    list_one_user,
    reset_user_password,
    update_user,
    delete_user
)
from src.views.usuarios_views import Usuario

router = APIRouter()


@router.post("/usuarios/", response_model=Usuario)
async def create_user_controller(user: Usuario):
    try:
        return await create_user(user)
    except HTTPException as e:
        return e


@router.get("/usuarios/", response_model=List[Usuario])
async def list_users_controller():
    return await list_users()


@router.get("/usuarios/{user_id}", response_model=Usuario)
async def get_user_controller(user_id: UUID):
    try:
        return await list_one_user(user_id)
    except HTTPException as e:
        return e


@router.put("/usuarios/{user_id}", response_model=Usuario)
async def update_user_controller(user_id: UUID, user: Usuario):
    try:
        return await update_user(user_id, user)
    except HTTPException as e:
        return e


@router.delete("/usuarios/{user_id}", response_model=Usuario)
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
