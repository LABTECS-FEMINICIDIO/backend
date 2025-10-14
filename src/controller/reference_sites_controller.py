from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from src.views.reference_sites_views import createReferenceSite, listAllREferenceSites, updatePesquisarField, updateReferenceSite
from typing import Dict

router = APIRouter()


class ReferenceSites(BaseModel):
    nome: str
    link: str


@router.post("/referenceSite/")
async def create_reference_sites_controller(reference_site: ReferenceSites):
    return await createReferenceSite(reference_site)


@router.get("/referenceSite/")
async def list_reference_sites_controller():
    return await listAllREferenceSites()


@router.patch("/referenceSitePesquisar/{site_id}")
async def update_reference_site_controller(site_id):
    return await updatePesquisarField(site_id)


@router.patch("/referenceSite/{site_id}")
async def update_reference_site_controller(site_id, item: Dict):
    return await updateReferenceSite(site_id, item)
