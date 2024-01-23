from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from src.views.sites_view import create_site, iml_screapper, list_iml, list_sites, list_one_site, update_site, delete_site, find_sites_with_keywords
import schedule
import time
import threading
from datetime import datetime
from src.views.search_schedule_views import list_agendamento_pesquisas
import asyncio
import json
from uuid import UUID
from src.model.models import VitimasModels
from typing import Dict
router = APIRouter()


class Vitima(BaseModel):
    id: UUID
    nome: str
    idade: int
    rua: str
    armaUsada: str
    # site_id: UUID


class Site(BaseModel):
    id: UUID
    nome: str
    link: str
    conteudo: Optional[str] = None
    feminicidio: Optional[bool] = None
    lido: Optional[bool] = None
    vitima: Optional[Vitima] = None

    class Config:
        arbitrary_types_allowed = True


class UpdateSite(BaseModel):
    nome: Optional[str]
    link: Optional[str]
    conteudo: Optional[str]
    feminicidio: Optional[bool]
    lido: Optional[bool]
    vitimas: Optional[Vitima]


@router.post("/site/", response_model=Site)
async def create_site_controller(site: Site):
    return await create_site(site)


@router.get("/site/")
async def list_sites_controller():
    return await list_sites()


@router.get("/site/{site_url}", response_model=Site)
async def list_one_site_controller(site_url: str):
    return await list_one_site(site_url)


@router.patch("/site/{siteId}")
async def update_site_controller(siteId: str, item: Dict):
    return await update_site(siteId, item)


@router.delete("/item/{siteId}", response_model=Site)
async def delete_site_controller(siteId: str):
    return await delete_site(siteId)

is_loop_running_iml = False
loop_task_iml = None

is_loop_running = False
loop_task = None


async def background_task_iml():
    global is_loop_running_iml
    while is_loop_running_iml:
        tempo = await list_agendamento_pesquisas()

        if tempo:
            tempo_agendado = tempo[0].dias
        else:
            tempo_agendado = 1

        await iml_screapper()
        await asyncio.sleep(tempo_agendado * 60)


async def background_task():
    global is_loop_running
    while is_loop_running:
        tempo = await list_agendamento_pesquisas()

        if tempo:
            tempo_agendado = tempo[0].dias
        else:
            tempo_agendado = 1

        await find_sites_with_keywords(tempo_agendado=tempo_agendado)
        await asyncio.sleep(tempo_agendado * 60)


@router.get("/iml/")
async def find_iml():
    global is_loop_running_iml, loop_task_iml

    # Inicia ou reinicia o loop de IML
    if not is_loop_running_iml:
        is_loop_running_iml = True
        loop_task_iml = asyncio.create_task(background_task_iml())

    return {"message": "Busca de dados no IML agendada com sucesso!"}


@router.get("/findSites/")
async def find_sites():
    global is_loop_running, loop_task

    # Inicia ou reinicia o loop de sites
    if not is_loop_running:
        is_loop_running = True
        loop_task = asyncio.create_task(background_task())

    return {"message": "Busca de sites agendada com sucesso!"}


@router.get("/imlData/")
async def find_iml_data():
    return list_iml()
