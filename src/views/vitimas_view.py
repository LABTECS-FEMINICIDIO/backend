from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from src.database.database import engine
from src.model.models import VitimasModels
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from uuid import UUID
from typing import List, Optional


class Vitima(BaseModel):
    nome: str
    idade: int
    rua: str
    armaUsada: str


class VitimaEdit(BaseModel):
    datadofato: Optional[str] = None
    diah: Optional[str] = None
    horario: Optional[str] = None
    turno: Optional[str] = None
    nome: Optional[str] = None
    idade: Optional[int] = None
    racacor1: Optional[str] = None
    estciv2: Optional[str] = None
    bairro: Optional[str] = None
    rua_beco_travessa_estrada_ramal: Optional[str] = None
    endcomplemento: Optional[str] = None
    tipoarma1: Optional[str] = None
    tipoarma2: Optional[str] = None
    loclesao1: Optional[str] = None
    loclesao2: Optional[str] = None
    loclesao3: Optional[str] = None
    hospitalizacao: Optional[str] = None
    violsexual: Optional[str] = None
    latrocinio: Optional[str] = None
    localdeocorrencia: Optional[str] = None
    presencafilhofamiliar: Optional[str] = None
    compexcomp: Optional[str] = None
    gestacao: Optional[str] = None
    filhosdescrever: Optional[str] = None
    lat: Optional[str] = None
    lng: Optional[str] = None


async def create_vitima(vitima: Vitima):
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()
    db_vitima = VitimasModels(**vitima.model_dump())
    db_session.add(db_vitima)
    db_session.commit()
    db_session.refresh(db_vitima)
    return jsonable_encoder(db_vitima)


async def list_vitimas():
    db = sessionmaker(bind=engine)
    db_session = db()
    vitimas = db_session.query(VitimasModels).options(
        joinedload(VitimasModels.sites)).all()

    return jsonable_encoder(vitimas)


async def list_one_vitima(vitima_id: UUID):
    db = sessionmaker(bind=engine)
    vitima = db.query(VitimasModels).filter(
        VitimasModels.id == vitima_id).first()
    if vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")
    return jsonable_encoder(vitima)


async def update_vitima(vitima_id: UUID, vitima: dict):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_vitima = db_session.query(VitimasModels).filter(
        VitimasModels.id == vitima_id).first()

    if db_vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")

    for key, value in vitima.items():
        setattr(db_vitima, key, value)

    db_session.commit()
    db_session.refresh(db_vitima)

    return jsonable_encoder(db_vitima)


async def delete_vitima(vitima_id: UUID, ):
    db = sessionmaker(bind=engine)
    db_vitima = db.query(VitimasModels).filter(
        VitimasModels.id == vitima_id).first()
    if db_vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")

    db.delete(db_vitima)
    db.commit()

    return jsonable_encoder(db_vitima)
