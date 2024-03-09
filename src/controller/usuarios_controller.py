from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID
import smtplib
from email.mime.text import MIMEText
import random
from dotenv import load_dotenv
import os
import string
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
    delete_user,
    change_password_with_recovery_code,
    clear_recovery_code,
    update_recovery_code,
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
    
load_dotenv()

def send_email(email_to: str, subject: str, body: str):
    EMAIL_HOST = 'smtp.office365.com'
    EMAIL_PORT = 587 

    EMAIL_USER =  os.getenv("EMAIL_RECOVERY")
    EMAIL_PASSWORD =  os.getenv("PASS_RECOVERY")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = email_to

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, [email_to], msg.as_string())

def generate_recovery_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class RecoveryRequest(BaseModel):
    email: str

@router.post("/recuperarSenha/")
async def recovery_password(data: RecoveryRequest):
        recovery_code = generate_recovery_code()
        update_recovery_code(data.email, recovery_code)
        subject = "Recuperação de senha"
        body = f"Seu código de recuperação é: {recovery_code}"
        send_email(data.email, subject, body)
        return {"message": "Um e-mail foi enviado com o código de recuperação."}

class ChangePasswordRequest(BaseModel):
    email: str
    recovery_code: str
    new_password: str

@router.post("/mudarSenha/")
def change_pass(request: ChangePasswordRequest):
        return change_password_with_recovery_code(request.email, request.recovery_code, request.new_password)
