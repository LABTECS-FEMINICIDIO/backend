from typing import Dict
from urllib.parse import urlparse
from fastapi import HTTPException
import requests
from fastapi.encoders import jsonable_encoder
from psycopg2 import IntegrityError
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker, joinedload
from typing import List, Optional, Union
from src.database.database import engine
from src.model.models import FeriadosModels, ReferenceSitesModels, SitesModels, ImlModels
from bs4 import BeautifulSoup
from src.views.tags_view import list_tags
from datetime import datetime
import random
import json

from src.views.reference_sites_views import createReferenceSiteForParse


class Site(BaseModel):
    nome: str
    link: str
    conteudo: Optional[str] = None
    feminicidio: Optional[bool] = None
    lido: Optional[bool] = False
    vitima: Optional[Dict] = None


class SiteUpdate(BaseModel):
    nome: Optional[str] = None
    link: Optional[str] = None
    conteudo: Optional[str] = None
    classificacao: Optional[int] = None,
    feminicidio: Optional[bool] = None
    lido: Optional[bool] = None


class Iml(BaseModel):
    dataEntrada: Optional[str] = None
    horaEntrada: Optional[str] = None
    sexo: Optional[str] = None
    idade: Optional[str] = None
    bairroDaRemocao: Optional[str] = None
    causaMorte: Optional[str] = None


async def create_site(site: Site, reference_site_link: str):
    if not link_exists(site.link):
        # raise HTTPException(
        #     status_code=409, detail="O link do site já está cadastrado."
        # )

        await createReferenceSiteForParse({
            "nome": site.nome,
            "link": reference_site_link,
            "linksEncontrados": 1
        })

        db_site = SitesModels(**site.model_dump())
        db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db_session = db()

        try:
            db_session.add(db_site)
            db_session.commit()
            db_session.refresh(db_site)
        except IntegrityError:
            db_session.rollback()
            raise HTTPException(
                status_code=409, detail={"message": "O link do site já está cadastrado."})
        finally:
            db_session.close()

        return site


async def list_sites():
    db = sessionmaker(bind=engine)
    db_session = db()

    sites = db_session.query(SitesModels).options(
        joinedload(SitesModels.vitima)).order_by(desc(SitesModels.createdAt)).all()
    db_session.close()
    return sites


async def list_one_site(url_site: str):
    db = sessionmaker(bind=engine)
    db_session = db()

    site_db = db_session.query(SitesModels).filter(
        SitesModels.link == url_site).first()

    db_session.close()

    if site_db is None:
        raise HTTPException(status_code=404, detail="Site not found")

    site = jsonable_encoder(site_db)

    return site


async def update_site(siteId: str, site_data: Dict):
    db = sessionmaker(bind=engine)
    db_session = db()

    db_site = db_session.query(SitesModels).filter(
        SitesModels.id == siteId).first()

    all_same_sites = db_session.query(SitesModels).filter(
        SitesModels.nome == db_site.nome)

    if db_site is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Site not found")

    if "classificacao" in site_data and site_data["classificacao"]:
        total_classificacao = 0
        total_sites = 0

        for site in all_same_sites:
            if site.classificacao > 0:
                total_sites += 1
                total_classificacao += int(site.classificacao)

        site_referencia = db_session.query(ReferenceSitesModels).filter(
            ReferenceSitesModels.nome == db_site.nome
        ).first()

        site_referencia.classificacao = int(
            site_data["classificacao"]) + total_classificacao / (total_sites + 1)

    for key, value in site_data.items():
        if hasattr(db_site, key):
            setattr(db_site, key, value)

    db_session.commit()
    db_session.refresh(db_site)
    db_session.close()

    updated_site = jsonable_encoder(db_site)

    return updated_site


async def delete_site(siteId: str):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_site = db_session.query(SitesModels).filter(
        SitesModels.id == siteId).first()
    if db_site is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Site not found")
    db_session.delete(db_site)
    db_session.commit()
    db_session.close()
    return db_site


def link_exists(link: str) -> bool:
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    existing_site = db_session.query(SitesModels).filter_by(link=link).first()

    db_session.close()

    return existing_site is not None


async def fetch_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser').prettify()
        else:
            print(f"Failed to fetch content from '{url}'")
            return None
    except Exception as e:
        print(f"Error fetching content from '{url}': {str(e)}")
        return None


async def find_sites_with_keywords(tempo_agendado):
    print("entrei no find sites")
    found_sites = []

    data = (str(datetime.now()).split(" ")[0].split("-"))

    int(data[2]) - 2

    data[2] = int(data[2]) - tempo_agendado

    if data[2] < 10:
        data[2] = "0"+str(data[2])
    else:
        data[2] = str(data[2])

    tags = await list_tags()

    # if len(tags) == 0:
    # raise HTTPException(status_code=404, detail="Nenhuma tag cadastrada")

    all_tags = [tag.nome for tag in tags]

    keywords = "+".join(all_tags)

    search_url = f'https://www.google.com/search?q={keywords}+after%3A{data[0]}%2F{data[1]}%2F{data[2]}'
    print("url", search_url)
    response = requests.get(search_url)
    print("google respondeu")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        search_results = soup.find_all('a')
    else:
        print(response)
        print(f"Failed to fetch search results for '{keywords}'")

    for result in search_results:
        if result and result.get('data-ved', ''):
            href = result.get('href')
            if href and href.startswith('/url?q='):
                url = href.split('/url?q=')[1].split('&sa=')[0]
                parsed_url = urlparse(url)
                site_name = parsed_url.netloc.replace(
                    "www.", "").split(".")[0]

                # await createReferenceSiteForParse({
                #     "nome": site_name,
                #     "link": parsed_url.netloc,
                #     "linksEncontrados": 1
                # })

                if url not in found_sites:
                    found_sites.append(
                        {'url': url, 'name': site_name, "reference_site_link": parsed_url.netloc})
    print("total encontrado", len(found_sites))
    for site_info in found_sites:
        site_blocked = site_is_blocked(site_name=site_info["name"])

        content = await fetch_content(site_info['url'])
        if site_blocked == True:
            await create_site(Site(
                nome=site_info['name'],
                link=site_info['url'],
                conteudo=content
            ), site_info['reference_site_link'])

            print('criei o site')

    return found_sites


async def iml_screapper():

    search_url = f'https://docs.google.com/spreadsheets/d/1y_KpXEZSOsIu8LHfie5-Uon3VkG_PBew5hm_C63EDUQ/edit#gid=0'

    response = requests.get(search_url)
    print('iml respondeu', response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # for script in soup(['script']):
        #    script.extract()

        table = soup.find('table')

        if table:
            for row in table.find_all('tr'):

                cells = row.find_all('td')
                content = []
                if cells:
                    for cell in cells:
                        content.append(cell.text)

                    if content[0] != "DATA DE ENTRADA":

                        if not check_if_all_array_items_is_blank(content):
                            if not is_duplicate_record(content):
                                await create_iml(Iml(
                                    dataEntrada=content[0],
                                    horaEntrada=content[1],
                                    sexo=content[2],
                                    idade=content[3],
                                    bairroDaRemocao=content[4],
                                    causaMorte=content[5]
                                ))

    else:
        print(response)


async def create_iml(iml: Iml):
    db_iml = ImlModels(**iml.model_dump())

    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    try:
        db_session.add(db_iml)
        db_session.commit()
        db_session.refresh(db_iml)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=409, detail={"message": "O registro já existe."}
        )
    finally:
        db_session.close()

    return iml


def check_if_all_array_items_is_blank(arr):
    if isinstance(arr, list):
        is_all_blank = all(element == "" for element in arr)
        return is_all_blank


def list_iml():
    db = sessionmaker(bind=engine)
    db_session = db()

    iml_data = db_session.query(ImlModels).all()
    db_session.close()
    return iml_data


def is_duplicate_record(content):
    db = sessionmaker(bind=engine)
    db_session = db()

    existing_record = db_session.query(ImlModels).filter_by(
        dataEntrada=content[0],
        horaEntrada=content[1],
        sexo=content[2],
        idade=content[3],
        bairroDaRemocao=content[4],
        causaMorte=content[5]
    ).first()

    db_session.close()

    return existing_record is not None


def site_is_blocked(site_name):
    db = sessionmaker(bind=engine)
    db_session = db()

    site = db_session.query(ReferenceSitesModels).filter(
        ReferenceSitesModels.nome == site_name).first()

    if site:
        return site.pesquisar
    else:
        return True


async def change_site_lido(site_id):
    db = sessionmaker(bind=engine)
    db_session = db()

    site = db_session.query(SitesModels).filter(
        SitesModels.id == site_id).first()

    site.lido = not site.lido

    db_session.commit()
    db_session.close()

    return site


# TODO:


def is_holiday(date):
    year_data = int(str(date).split(" ")[0].split("-")[0])
    month_data = int(str(date).split(" ")[0].split("-")[1])
    day_data = int(str(date).split(" ")[0].split("-")[2])

    db = sessionmaker(bind=engine)
    db_session = db()

    holiday = db_session.query(FeriadosModels).filter_by(
        FeriadosModels.year == year_data,
        FeriadosModels.month == month_data,
        FeriadosModels.day == day_data
    )

    return holiday is not None
