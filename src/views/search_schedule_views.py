from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import sessionmaker
from src.database.database import engine
from src.model.models import AgendamentoPesquisaModels
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class AgendamentoPesquisa(BaseModel):
    dias: int


class AgendamentoPesquisaUpdate(BaseModel):
    dias: Optional[int] = None


async def create_or_update_agendamento_pesquisa(agendamento_pesquisa: AgendamentoPesquisa):
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    try:
        existing_agendamento_pesquisa = db_session.query(
            AgendamentoPesquisaModels).first()

        if existing_agendamento_pesquisa:
            # Atualiza o registro existente
            update_data = agendamento_pesquisa.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(existing_agendamento_pesquisa, key, value)
            db_session.commit()
            db_session.refresh(existing_agendamento_pesquisa)
            return existing_agendamento_pesquisa
        else:
            # Cria um novo registro
            db_agendamento_pesquisa = AgendamentoPesquisaModels(
                **agendamento_pesquisa.model_dump())
            db_session.add(db_agendamento_pesquisa)
            db_session.commit()
            db_session.refresh(db_agendamento_pesquisa)
            return agendamento_pesquisa
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar/atualizar agendamento de pesquisa: {str(e)}")
    finally:
        db_session.close()


async def list_agendamento_pesquisas():
    db = sessionmaker(bind=engine)
    db_session = db()
    agendamentos_pesquisa = db_session.query(AgendamentoPesquisaModels).all()
    db_session.close()
    return agendamentos_pesquisa


async def get_agendamento_pesquisa(agendamento_pesquisa_id: UUID):
    db = sessionmaker(bind=engine)
    db_session = db()

    agendamento_pesquisa_db = db_session.query(AgendamentoPesquisaModels).filter(
        AgendamentoPesquisaModels.id == agendamento_pesquisa_id).first()

    db_session.close()

    if agendamento_pesquisa_db is None:
        raise HTTPException(
            status_code=404, detail="Agendamento de pesquisa não encontrado")

    agendamento_pesquisa = jsonable_encoder(agendamento_pesquisa_db)

    return agendamento_pesquisa


async def update_agendamento_pesquisa(agendamento_pesquisa_id: UUID, agendamento_pesquisa: AgendamentoPesquisa):
    db = sessionmaker(bind=engine)
    db_session = db()

    db_agendamento_pesquisa = db_session.query(AgendamentoPesquisaModels).filter(
        AgendamentoPesquisaModels.id == agendamento_pesquisa_id).first()

    if db_agendamento_pesquisa is None:
        db_session.close()
        raise HTTPException(
            status_code=404, detail="Agendamento de pesquisa não encontrado")

    for key, value in agendamento_pesquisa.model_dump().items():
        setattr(db_agendamento_pesquisa, key, value)

    db_session.commit()
    db_session.refresh(db_agendamento_pesquisa)
    db_session.close()

    updated_agendamento_pesquisa = jsonable_encoder(db_agendamento_pesquisa)

    return updated_agendamento_pesquisa


async def delete_agendamento_pesquisa(agendamento_pesquisa_id: UUID):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_agendamento_pesquisa = db_session.query(AgendamentoPesquisaModels).filter(
        AgendamentoPesquisaModels.id == agendamento_pesquisa_id).first()

    if db_agendamento_pesquisa is None:
        db_session.close()
        raise HTTPException(
            status_code=404, detail="Agendamento de pesquisa não encontrado")

    db_session.delete(db_agendamento_pesquisa)
    db_session.commit()
    db_session.close()

    return db_agendamento_pesquisa
