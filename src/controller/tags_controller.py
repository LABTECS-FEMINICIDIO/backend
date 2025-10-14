from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from src.views.tags_view import create_tag, list_tags, list_one_tag, update_tag, delete_tag

router = APIRouter()


class Tag(BaseModel):
    nome: str


@router.get("/ping/")
async def ping():
    return "pong"


@router.post("/tag/", response_model=Tag)
async def create_tag_controller(tag: Tag):
    return await create_tag(tag)


@router.get("/tag/", response_model=List[Tag])
async def list_tags_controller():
    return await list_tags()


@router.get("/tag/{tag_name}", response_model=Tag)
async def list_one_tag_controller(tag_name: str):
    return await list_one_tag(tag_name)


@router.patch("/tag/{tag_name}", response_model=Tag)
async def update_tag_controller(tag_name: str, item: Tag):
    return await update_tag(tag_name, item)


@router.delete("/tag/{tag_name}", response_model=Tag)
async def delete_tag_controller(tag_name: str):
    return await delete_tag(tag_name)
