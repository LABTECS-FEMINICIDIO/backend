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

# Fazer a pesquisa de 2 em 2 dias por exemplo, aqui devo salvar o tempo em irei fazer as buscas


class AgendamentoPesquisaModels(Base):
    __tablename__ = "agendamentoPesquisa"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    dias = Column(Integer, unique=True)

# Aqui irei colocar o tempo em que olharei para "atras" na pesquisa, por exemplo, quero ver até notícias de 2 dias atrás


class PeriodoPesquisaModels(Base):
    __tablename__ = "periodoPesquisa"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    dias = Column(Integer, unique=True)


class UsuariosModels(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True)
    telefone = Column(String)
    senha = Column(String)
    acesso = Column(Boolean)
