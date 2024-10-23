from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from src.database.database import engine
from src.model.models import VitimasModels
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from uuid import UUID
from typing import List, Optional
from sqlalchemy import asc, desc
from datetime import datetime

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
    sites_in_bulk: Optional[str] = None


async def create_vitima(vitima: dict):
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    if 'lat' in vitima and vitima['lat'] is not None:
        vitima['lat'] = f"{float(vitima['lat']):.5f}"
    if 'lng' in vitima and vitima['lng'] is not None:
        vitima['lng'] = f"{float(vitima['lng']):.5f}"

    db_vitima = VitimasModels(**vitima.model_dump())
    db_session.add(db_vitima)
    db_session.commit()
    db_session.refresh(db_vitima)
    return jsonable_encoder(db_vitima)


async def list_vitimas():
    db = sessionmaker(bind=engine)
    db_session = db()
    vitimas = db_session.query(VitimasModels).options(
        joinedload(VitimasModels.sites)).order_by(desc(VitimasModels.datadofato)).all()

    return jsonable_encoder(vitimas)

async def list_vitimas_for_export():
    db = sessionmaker(bind=engine)
    db_session = db()
    vitimas = db_session.query(VitimasModels).options(
        joinedload(VitimasModels.sites)
    ).order_by(asc(VitimasModels.idade)).all()

    # Prepara os dados para exportação
    vitimas_data = []
    for vitima in vitimas:
        vitima_dict = jsonable_encoder(vitima)
        
        # Converte o createdAt para datetime
        if vitima_dict.get("createdAt"):
            created_at = datetime.strptime(vitima_dict["createdAt"], "%Y-%m-%d %H:%M:%S")  # Ajuste o formato se necessário
            vitima_dict["DataCaptura"] = created_at.date().strftime("%Y-%m-%d")  # Extrai apenas a data
            vitima_dict["HoraCaptura"] = created_at.time().strftime("%H:%M:%S")  # Extrai apenas a hora
        else:
            vitima_dict["DataCaptura"] = ""
            vitima_dict["HoraCaptura"] = ""

        vitimas_data.append(vitima_dict)

    return vitimas_data

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
    db_session = db()
    db_vitima = db_session.query(VitimasModels).filter(
        VitimasModels.id == vitima_id).first()
    if db_vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")

    db_session.delete(db_vitima)
    db_session.commit()

    return jsonable_encoder(db_vitima)

async def list_one_vitima(vitima_id: UUID):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_vitima = db_session.query(VitimasModels).filter(
        VitimasModels.id == vitima_id).first()
    if db_vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")

    return jsonable_encoder(db_vitima)