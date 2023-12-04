from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from src.views.sites_view import create_site, list_sites, list_one_site, update_site, delete_site, find_sites_with_keywords

router = APIRouter()


class Site(BaseModel):
    nome: str
    link: str
    conteudo: Optional[str] = None
    feminicidio: Optional[bool] = None
    lido: Optional[bool] = None

# TODO:


@router.get("/findSites/")
async def find_sites():
    return await find_sites_with_keywords()


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
