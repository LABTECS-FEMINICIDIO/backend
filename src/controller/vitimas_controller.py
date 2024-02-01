from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from src.views.vitimas_view import VitimaEdit, create_vitima, delete_vitima, list_vitimas, update_vitima
router = APIRouter()


class Vitima(BaseModel):
    datadofato: str
    diah: str
    horario: str
    turno: str
    nome: str
    idade: int
    racacor1: str
    estciv2: str
    bairro: str
    rua_beco_travessa_estrada_ramal: str
    endcomplemento: str
    tipoarma1: str
    tipoarma2: str
    loclesao1: str
    loclesao2: str
    loclesao3: str
    hospitalizacao: str
    violsexual: str
    latrocinio: str
    zona: str
    localdeocorrencia: str
    presencafilhofamiliar: str
    gestacao: str
    filhosdescrever: int
    sites: Optional[List[UUID]] = []


@router.post("/vitimas/", response_model=Vitima)
async def create_vitimas_controller(vitima: Vitima):
    return await create_vitima(vitima)


@router.get("/vitimas/")
async def list_tags_controller():
    return await list_vitimas()


# @router.get("/tag/{tag_name}", response_model=Tag)
# async def list_one_tag_controller(tag_name: str):
#     return await list_one_tag(tag_name)


@router.patch("/vitimas/{vitima_id}")
async def update_vitima_controller(vitima_id, item: dict):
    return await update_vitima(vitima_id, item)


@router.delete("/vitimas/{vitima_id}")
async def delete_vitimas_controller(vitima_id: str):
    return await delete_vitima(vitima_id)
