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


async def import_xlsx_file(file: UploadFile):
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Arquivo inválido")

    wb = load_workbook(file.file)
    ws = wb.active

    rows = list(ws.rows)
    if not rows:
        raise HTTPException(status_code=400, detail="Planilha vazia")

    headers = [cell.value for cell in rows[0]]

    # colunas válidas do model
    valid_columns = {col.name for col in VitimasModels.__table__.columns}

    registros_criados = 0

    for row in rows[1:]:
        row_data = {}

        for header, cell in zip(headers, row):
            if header not in valid_columns or header == "id":
                continue

        value = cell.value

        if value in ("", None):
            row_data[header] = None
        elif header == "datadofato":
            row_data[header] = parse_to_date(value)
        else:
            row_data[header] = value

        # força NULL para colunas do model que não vieram na planilha
        for col in valid_columns:
            if col != "id" and col not in row_data:
                row_data[col] = None

        novo = VitimasModels(**row_data)
        db_session.add(novo)
        registros_criados += 1

    db_session.commit()

    return {"message": "Importação concluída", "registros_inseridos": registros_criados}


async def create_vitima(vitima: dict):
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    if "lat" in vitima and vitima["lat"] is not None:
        vitima["lat"] = f"{float(vitima['lat']):.5f}"
    if "lng" in vitima and vitima["lng"] is not None:
        vitima["lng"] = f"{float(vitima['lng']):.5f}"

    db_vitima = VitimasModels(**vitima.model_dump())
    db_session.add(db_vitima)
    db_session.commit()
    db_session.refresh(db_vitima)
    return jsonable_encoder(db_vitima)


async def list_vitimas():
    db = sessionmaker(bind=engine)
    db_session = db()
    vitimas = (
        db_session.query(VitimasModels)
        .options(joinedload(VitimasModels.sites))
        .order_by(desc(VitimasModels.datadofato))
        .all()
    )

    return jsonable_encoder(vitimas)


async def list_vitimas_for_export():
    db = sessionmaker(bind=engine)
    db_session = db()
    vitimas = (
        db_session.query(VitimasModels)
        .options(joinedload(VitimasModels.sites))
        .order_by(asc(VitimasModels.idade))
        .all()
    )

    return jsonable_encoder(vitimas)


async def list_one_vitima(vitima_id: UUID):
    db = sessionmaker(bind=engine)
    vitima = db.query(VitimasModels).filter(VitimasModels.id == vitima_id).first()
    if vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")
    return jsonable_encoder(vitima)


async def update_vitima(vitima_id: UUID, vitima: dict):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_vitima = (
        db_session.query(VitimasModels).filter(VitimasModels.id == vitima_id).first()
    )

    if db_vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")

    for key, value in vitima.items():
        setattr(db_vitima, key, value)

    db_session.commit()
    db_session.refresh(db_vitima)

    return jsonable_encoder(db_vitima)


async def delete_vitima(
    vitima_id: UUID,
):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_vitima = (
        db_session.query(VitimasModels).filter(VitimasModels.id == vitima_id).first()
    )
    if db_vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")

    db_session.delete(db_vitima)
    db_session.commit()

    return jsonable_encoder(db_vitima)


async def list_one_vitima(vitima_id: UUID):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_vitima = (
        db_session.query(VitimasModels).filter(VitimasModels.id == vitima_id).first()
    )
    if db_vitima is None:
        raise HTTPException(status_code=404, detail="Vítima not found")

    return jsonable_encoder(db_vitima)
