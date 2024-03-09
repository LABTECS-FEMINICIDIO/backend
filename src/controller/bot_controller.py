from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.views.sites_view import change_site_lido, create_site, iml_screapper, list_iml, list_sites, list_one_site, update_site, delete_site, find_sites_with_keywords, parse_excel
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
from openpyxl import load_workbook
from src.views.historySearch_views import get_latest_history_search, createHistorySearch

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
    # conteudo: Optional[str] = None
    feminicidio: Optional[bool] = None
    lido: Optional[bool] = None
    vitima: Optional[Vitima] = None

    class Config:
        arbitrary_types_allowed = True

class SiteComplet(BaseModel):
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

@router.post("/uploadIml")
async def analyze_excel(file: UploadFile = File(...)):
    try:
        response_data = await parse_excel(file=file)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar o arquivo: {str(e)}")

@router.get("/site/")
async def list_sites_controller():
    return await list_sites()


@router.get("/site/{id}", response_model=SiteComplet)
async def list_one_site_controller(id: str):
    return await list_one_site(id)


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
        # tempo = await list_agendamento_pesquisas()

        # if tempo:
        #     tempo_agendado = tempo[0].dias
        # else:
        #     tempo_agendado = 1

        await iml_screapper()
        await asyncio.sleep(1 * 86400)


async def background_task():
    global is_loop_running
    print("to no começo do backfround task")
    print(is_loop_running)
    while is_loop_running:
        tempo = await list_agendamento_pesquisas()

        if tempo:
            tempo_agendado = tempo[0].dias
        else:
            tempo_agendado = 5
            
        print("ENTREI NA BACGROUND TASK")

        # await find_sites_with_keywords(tempo_agendado=tempo_agendado)
        # await createHistorySearch()
        
        await asyncio.sleep(tempo_agendado * 10)


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
    tempo = await list_agendamento_pesquisas()

    if tempo:
        tempo_agendado = tempo[0].dias
    else:
        tempo_agendado = 5

    # await find_sites_with_keywords(tempo_agendado=tempo_agendado)
    # Inicia ou reinicia o loop de sites
        print("AAAAAAAAAA", is_loop_running)
        print(not is_loop_running)

    if not is_loop_running:
        is_loop_running = True
        print("entrei no if")
        loop_task = asyncio.create_task(background_task)
    # await createHistorySearch()
    return {"message": "Busca de sites agendada com sucesso!"}


@router.get("/imlData/")
async def find_iml_data():
    return await list_iml()


@router.patch("/updateLido/{siteId}")
async def update_lido(siteId: str):
    return await change_site_lido(siteId)

@router.get("/history/lastSearch")
async def last_search():
    return await get_latest_history_search()