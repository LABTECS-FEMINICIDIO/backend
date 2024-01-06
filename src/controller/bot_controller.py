from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from src.views.sites_view import create_site, list_sites, list_one_site, update_site, delete_site, find_sites_with_keywords
import schedule
import time
import threading
from datetime import datetime
from src.views.search_schedule_views import list_agendamento_pesquisas
import asyncio
import json
from uuid import UUID
from src.model.models import VitimasModels

router = APIRouter()


class Vitima(BaseModel):
    id: UUID
    nome: str
    idade: int
    rua: str
    armaUsada: str
    site_id: UUID


class Site(BaseModel):
    id: UUID
    nome: str
    link: str
    conteudo: Optional[str] = None
    feminicidio: Optional[bool] = None
    lido: Optional[bool] = None
    vitimas: List[Vitima]

    class Config:
        arbitrary_types_allowed = True

# TODO:


def job():
    print("entrei no job")
    find_sites_with_keywords()
    # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # log_message = f"Executando a tarefa em: {current_time}"
    # with open("log.txt", "a") as log_file:
    #     log_file.write(log_message + "\n")


async def loop():
    tempo = await list_agendamento_pesquisas()

    if tempo:
        tempo_agendado = tempo[0].dias
    else:
        tempo_agendado = 1

    # schedule.every(tempo_agendado).seconds.do(job)

    while True:
        # schedule.run_pending()
        await find_sites_with_keywords()
        time.sleep(tempo_agendado * 60)

is_loop_running = False
loop_task = None


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


@router.get("/findSites/")
async def find_sites(background_tasks: BackgroundTasks):
    global is_loop_running, loop_task

    # Verifica se o loop está em execução e o interrompe
    if is_loop_running:
        is_loop_running = False
        loop_task.cancel()

    # Inicia um novo loop
    is_loop_running = True
    loop_task = asyncio.create_task(background_task())

    return {"message": "Busca de sites agendada com sucesso!"}


@router.post("/site/", response_model=Site)
async def create_site_controller(site: Site):
    return await create_site(site)


@router.get("/site/", response_model=List[Site])
async def list_sites_controller():
    return await list_sites()


@router.get("/site/{site_url}", response_model=Site)
async def list_one_site_controller(site_url: str):
    return await list_one_site(site_url)


@router.patch("/site/{site_url}", response_model=Site)
async def update_site_controller(site_url: str, item: Site):
    return await update_site(site_url, item)


@router.delete("/item/{site_url}", response_model=Site)
async def delete_site_controller(site_url: str):
    return await delete_site(site_url)


# def job():
#     print("oi papai")


# async def loop():
#     tempo = await list_agendamento_pesquisas()

#     if tempo:
#         tempo_agendado = tempo[0].dias
#     else:
#         tempo_agendado = 1

#     schedule.every(tempo_agendado).minutes.do(job)

#     while True:
#         schedule.run_pending()
#         time.sleep(5)


# @router.post("/teste")
# async def teste():
#     schedule.clear()

#     loop_thread = threading.Thread(target=lambda: asyncio.run(loop()))
#     loop_thread.start()

#     return "oi"
