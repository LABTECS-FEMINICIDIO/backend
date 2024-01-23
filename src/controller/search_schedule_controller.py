from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from src.views.search_schedule_views import create_or_update_agendamento_pesquisa, list_agendamento_pesquisas, get_agendamento_pesquisa, update_agendamento_pesquisa, delete_agendamento_pesquisa
from uuid import UUID

router = APIRouter()


class AgendamentoPesquisa(BaseModel):
    dias: int


@router.post("/agendamento-pesquisa/", response_model=AgendamentoPesquisa)
async def create_agendamento_pesquisa_controller(agendamento_pesquisa: AgendamentoPesquisa):
    return await create_or_update_agendamento_pesquisa(agendamento_pesquisa)


@router.get("/agendamento-pesquisa/", response_model=List[AgendamentoPesquisa])
async def list_agendamento_pesquisas_controller():
    return await list_agendamento_pesquisas()


@router.get("/agendamento-pesquisa/{agendamento_pesquisa_id}", response_model=AgendamentoPesquisa)
async def get_agendamento_pesquisa_controller(agendamento_pesquisa_id: UUID):
    return await get_agendamento_pesquisa(agendamento_pesquisa_id)


@router.patch("/agendamento-pesquisa/{agendamento_pesquisa_id}", response_model=AgendamentoPesquisa)
async def update_agendamento_pesquisa_controller(agendamento_pesquisa_id: UUID, item: AgendamentoPesquisa):
    return await update_agendamento_pesquisa(agendamento_pesquisa_id, item)


@router.delete("/agendamento-pesquisa/{agendamento_pesquisa_id}", response_model=AgendamentoPesquisa)
async def delete_agendamento_pesquisa_controller(agendamento_pesquisa_id: UUID):
    return await delete_agendamento_pesquisa(agendamento_pesquisa_id)
