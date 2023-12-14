from sqlalchemy import Column, Integer, String, Boolean
from src.database.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class SitesModels(Base):
    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    nome = Column(String)
    link = Column(String, unique=True)
    conteudo = Column(String, nullable=True)
    feminicidio = Column(Boolean, nullable=True)
    lido = Column(Boolean, nullable=True, default=False)


class TagsModels(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    nome = Column(String, unique=True)


class VitimasModels(Base):
    __tablename__ = "vitimas"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    nome = Column(String, unique=True)
