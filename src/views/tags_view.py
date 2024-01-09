from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg2 import IntegrityError
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from src.database.database import engine
from src.model.models import TagsModels


class Tag(BaseModel):
    nome: str


async def create_tag(tag: Tag):
    if tags_exists(tag.nome):
        raise HTTPException(
            status_code=409, detail=f"A tag {tag.nome} já está cadastrada."
        )

    da_tag = TagsModels(**tag.model_dump())
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    try:
        db_session.add(da_tag)
        db_session.commit()
        db_session.refresh(da_tag)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=409, detail=f"A tag {tag.nome} já está cadastrada.")
    finally:
        db_session.close()

    return tag


async def list_tags():
    db = sessionmaker(bind=engine)
    db_session = db()
    tags = db_session.query(TagsModels).all()
    db_session.close()
    return tags


async def list_one_tag(tag: str):
    db = sessionmaker(bind=engine)
    db_session = db()

    tag_db = db_session.query(TagsModels).filter(
        TagsModels.nome == tag).first()

    db_session.close()

    if tag_db is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag = jsonable_encoder(tag_db)

    return tag


async def update_tag(nome_tag: str, tag: Tag):
    db = sessionmaker(bind=engine)
    db_session = db()

    db_tag = db_session.query(TagsModels).filter(
        TagsModels.nome == nome_tag).first()

    if db_tag is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Tag not found")

    for key, value in tag.model_dump().items():
        setattr(db_tag, key, value)

    db_session.commit()

    db_session.refresh(db_tag)

    db_session.close()

    updated_tag = jsonable_encoder(db_tag)

    return updated_tag


async def delete_tag(tag: str):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_tag = db_session.query(TagsModels).filter(
        TagsModels.nome == tag).first()
    if db_tag is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Tag not found")
    db_session.delete(db_tag)
    db_session.commit()
    db_session.close()
    return db_tag


def tags_exists(nome: str) -> bool:
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    existing_site = db_session.query(TagsModels).filter_by(nome=nome).first()

    db_session.close()

    return existing_site is not None

# TODO:


def bot_find_sites():
    return None
