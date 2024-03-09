from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from src.database.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta


class SitesModels(Base):
    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    nome = Column(String)
    link = Column(String, unique=True)
    conteudo = Column(String, nullable=True)
    feminicidio = Column(Boolean, nullable=True)
    lido = Column(Boolean, nullable=True, default=False)
    classificacao = Column(Integer, default=0)
    valido = Column(Boolean, nullable=True)
    inHoliday = Column(Boolean, default=False)
    inWeekend = Column(Boolean, default=False)
    tagsEncontradas = Column(String, nullable=True)


    vitima_id = Column(UUID(as_uuid=True), ForeignKey(
        'vitimas.id'), nullable=True)
    vitima = relationship('VitimasModels', back_populates='sites')
    createdAt = Column(String, default=func.now())


class ReferenceSitesModels(Base):
    __tablename__ = "referenceSites"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    nome = Column(String)
    link = Column(String)
    pesquisar = Column(Boolean, default=True)
    linksEncontrados = Column(Integer, default=0)
    blocked = Column(Boolean, default=False)
    classificacao = Column(Integer, default=0)


class VitimasModels(Base):
    __tablename__ = "vitimas"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    datadofato = Column(String)
    diah = Column(String)
    horario = Column(String)
    turno = Column(String)
    nome = Column(String)
    idade = Column(Integer)
    racacor1 = Column(String)
    estciv2 = Column(String)
    bairro = Column(String)
    rua_beco_travessa_estrada_ramal = Column(String)
    endcomplemento = Column(String)
    tipoarma1 = Column(String)
    tipoarma2 = Column(String)
    loclesao1 = Column(String)
    loclesao2 = Column(String)
    loclesao3 = Column(String)
    hospitalizacao = Column(String)
    violsexual = Column(String)
    latrocinio = Column(String)
    localdeocorrencia = Column(String)
    presencafilhofamiliar = Column(String)
    compexcomp = Column(String)
    zona = Column(String)
    gestacao = Column(String)
    filhosdescrever = Column(String)
    lat = Column(String)
    lng = Column(String)
    sites = relationship('SitesModels', back_populates='vitima')
    createdAt = Column(String, default=func.now())


class TagsModels(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    nome = Column(String, unique=True)


class AgendamentoPesquisaModels(Base):
    __tablename__ = "agendamentoPesquisa"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    dias = Column(Integer, unique=True)


class PeriodoPesquisaModels(Base):
    __tablename__ = "periodoPesquisa"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    dias = Column(Integer, unique=True)

class HistorySearchModels(Base):
    __tablename__ = "historicoPesquisa"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    createdAt = Column(String, default=func.now())

class UsuariosModels(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True)
    telefone = Column(String)
    senha = Column(String)
    acesso = Column(Boolean)
    perfil = Column(String)
    recovery_code = Column(String, nullable=True)
    createdAt = Column(String, default=func.now())
    recovery_code_created_at = Column(DateTime, nullable=True)


class ImlModels(Base):
    __tablename__ = "iml"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    dataEntrada = Column(String, nullable=True)
    horaEntrada = Column(String, nullable=True)
    sexo = Column(String, nullable=True)
    idade = Column(String, nullable=True)
    bairroDaRemocao = Column(String, nullable=True)
    causaMorte = Column(String, nullable=True)


class FeriadosModels(Base):
    __tablename__ = "feriados"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                primary_key=True, index=True)
    ano = Column(Integer)
    mes = Column(Integer)
    dia = Column(Integer)
    tipo = Column(String)
