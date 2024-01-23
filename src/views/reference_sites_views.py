from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg2 import IntegrityError
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from src.database.database import engine
from src.model.models import ReferenceSitesModels
from typing import Dict


async def createReferenceSite(referenceSite):

    db_reference_site = ReferenceSitesModels(**referenceSite.model_dump())
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    reference_site_already_exists = db_session.query(
        ReferenceSitesModels).filter_by(nome=referenceSite.nome).first()

    if reference_site_already_exists:
        raise HTTPException(
            status_code=409, detail=f"A tag {referenceSite.nome} já está cadastrada."
        )

    try:
        db_session.add(db_reference_site)
        db_session.commit()
        db_session.refresh(db_reference_site)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=409, detail=f"A tag {referenceSite.nome} já está cadastrada."
        )
    finally:
        db_session.close()

    return referenceSite


async def listAllREferenceSites():
    db = sessionmaker(bind=engine)
    db_session = db()

    referenceSites = db_session.query(ReferenceSitesModels).all()
    db_session.close()
    return referenceSites


async def updatePesquisarField(site_id):
    db = sessionmaker(bind=engine)
    db_session = db()

    site = db_session.query(ReferenceSitesModels).filter_by(id=site_id).first()

    if site:
        site.pesquisar = not site.pesquisar
        db_session.commit()

    db_session.close()
    return {
        "message": "Site atualizado com sucesso."
    }


async def updateReferenceSite(site_id,  site_data: Dict):
    db = sessionmaker(bind=engine)
    db_session = db()

    site = db_session.query(ReferenceSitesModels).filter_by(id=site_id).first()

    for key, value in site_data.items():
        if hasattr(site, key):
            setattr(site, key, value)

    db_session.commit()
    db_session.close()
    return {
        "message": "Site atualizado com sucesso."
    }


async def site_reference_already_exists(nome):
    db = sessionmaker(bind=engine)
    db_session = db()

    site = db_session.query(ReferenceSitesModels).filter_by(nome=nome).first()

    if site:
        return True

    return False


async def createReferenceSiteForParse(referenceSite):
    db_reference_site = ReferenceSitesModels(**referenceSite)
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    reference_site_already_exists = db_session.query(
        ReferenceSitesModels).filter_by(nome=referenceSite.get("nome")).first()

    if reference_site_already_exists:
        reference_site_already_exists.linksEncontrados = reference_site_already_exists.linksEncontrados + 1
        db_session.commit()
        db_session.close()
        return

    try:
        db_session.add(db_reference_site)
        db_session.commit()
        db_session.refresh(db_reference_site)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=409, detail=f"A tag {referenceSite.get('nome')} já está cadastrada."
        )
    finally:
        db_session.close()

    return referenceSite
