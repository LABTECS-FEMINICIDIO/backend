from urllib.parse import urlparse
from fastapi import HTTPException
import requests
from fastapi.encoders import jsonable_encoder
from psycopg2 import IntegrityError
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from src.database.database import engine
from src.model.models import SitesModels
from bs4 import BeautifulSoup
from src.views.tags_view import list_tags
from datetime import datetime
import random


class Site(BaseModel):
    nome: str
    link: str
    conteudo: Optional[str] = None
    feminicidio: Optional[bool] = None
    lido: Optional[bool] = False


class SiteUpdate(BaseModel):
    nome: Optional[str] = None
    link: Optional[str] = None
    conteudo: Optional[str] = None
    feminicidio: Optional[bool] = None
    lido: Optional[bool] = None


async def create_site(site: Site):
    if not link_exists(site.link):
        # raise HTTPException(
        #     status_code=409, detail="O link do site já está cadastrado."
        # )

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
    sites = db_session.query(SitesModels).all()
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


async def update_site(url_site: str, site: SiteUpdate):
    db = sessionmaker(bind=engine)
    db_session = db()

    db_site = db_session.query(SitesModels).filter(
        SitesModels.nome == url_site).first()

    if db_site is None:
        db_session.close()
        raise HTTPException(status_code=404, detail="Site not found")

    for key, value in site.model_dump().items():
        setattr(db_site, key, value)

    db_session.commit()

    db_session.refresh(db_site)

    db_session.close()

    updated_site = jsonable_encoder(db_site)

    return updated_site


async def delete_site(url_site: str):
    db = sessionmaker(bind=engine)
    db_session = db()
    db_site = db_session.query(SitesModels).filter(
        SitesModels.link == url_site).first()
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

    if len(tags) == 0:
        raise HTTPException(status_code=404, detail="Nenhuma tag cadastrada")

    all_tags = [tag.nome for tag in tags]

    # acc = 0
    # TODO: aparentemente embaralhar as tags não adianta muita coisa
    # while acc < 4:
    # print("tags novas", all_tags)
    # print("data", data)
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

                if url not in found_sites:
                    found_sites.append({'url': url, 'name': site_name})

    for site_info in found_sites:
        await create_site(Site(
            nome=site_info['name'],
            link=site_info['url']
        ))

    # random.shuffle(all_tags)
    # print("embaralhando", all_tags)
    # acc += 1

    return found_sites
