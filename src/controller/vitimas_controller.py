from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from src.views.vitimas_view import create_vitima, list_vitimas
router = APIRouter()


class Vitima(BaseModel):
    nome: str
    idade: int
    rua: str
    armaUsada: str
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


# @router.patch("/tag/{tag_name}", response_model=Tag)
# async def update_tag_controller(tag_name: str, item: Tag):
#     return await update_tag(tag_name, item)


# @router.delete("/tag/{tag_name}", response_model=Tag)
# async def delete_tag_controller(tag_name: str):
#     return await delete_tag(tag_name)
