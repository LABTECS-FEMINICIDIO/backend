from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg2 import IntegrityError
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from src.database.database import engine
from src.model.models import FeriadosModels, TagsModels


class Feriado(BaseModel):
    ano: int
    mes: int
    dia: int


async def create_feriado(feriado: Feriado):
    if feriado_already_exits(feriado):
        raise HTTPException(
            status_code=409, detail=f"O feriado já está cadastrado."
        )

    db_feriado = FeriadosModels(**feriado.model_dump())
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    try:
        db_session.add(db_feriado)
        db_session.commit()
        db_session.refresh(db_feriado)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=409, detail=f"O feriado já está cadastrado.")
    finally:
        db_session.close()

    return db_feriado


async def list_feriados():
    db = sessionmaker(bind=engine)
    db_session = db()
    feriados = db_session.query(FeriadosModels).all()
    db_session.close()
    return feriados


# async def list_one_feriado(tag: str):
#     db = sessionmaker(bind=engine)
#     db_session = db()

#     tag_db = db_session.query(TagsModels).filter(
#         TagsModels.nome == tag).first()

#     db_session.close()

#     if tag_db is None:
#         raise HTTPException(status_code=404, detail="Tag not found")

#     tag = jsonable_encoder(tag_db)

#     return tag


async def update_feriado(feriado: Feriado):
    db = sessionmaker(bind=engine)
    db_session = db()

    db_feriado = db_session.query(FeriadosModels).filter_by(
        ano=feriado.ano,
        mes=feriado.mes,
        dia=feriado.dia
    ).first()

    if db_feriado is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Feriado not found")

    for key, value in feriado.model_dump().items():
        setattr(db_feriado, key, value)

    db_session.commit()

    db_session.refresh(db_feriado)

    db_session.close()

    updated_tag = jsonable_encoder(db_feriado)

    return updated_tag


async def delete_feriado(feriado_id):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_feriado = db_session.query(FeriadosModels).filter(
        FeriadosModels.id == feriado_id).first()
    if db_feriado is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Feriado not found")
    db_session.delete(db_feriado)
    db_session.commit()
    db_session.close()
    return db_feriado


def feriado_already_exits(feriado: Feriado) -> bool:
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    existing_feriado = db_session.query(FeriadosModels).filter_by(
        ano=feriado.ano,
        mes=feriado.mes,
        dia=feriado.dia
    ).first()

    db_session.close()

    return existing_feriado is not None
