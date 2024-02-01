from fastapi import APIRouter

from views.feriados_views import Feriado, create_feriado, delete_feriado, list_feriados, update_feriado

router = APIRouter()


@router.post("/feriados/")
async def create_feriados_controller(tag: Feriado):
    return await create_feriado(tag)


@router.get("/feriados/")
async def list_feriados_controller():
    return await list_feriados()


@router.patch("/feriados/")
async def update_feriado_controller(feriado: Feriado):
    return await update_feriado(feriado)


@router.delete("/feriados/{id}")
async def delete_tag_controller(id: str):
    return await delete_feriado(id)
