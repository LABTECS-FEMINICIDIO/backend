from urllib.parse import urlparse
from fastapi import HTTPException
import requests
from fastapi.encoders import jsonable_encoder
from psycopg2 import IntegrityError
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, joinedload
from typing import List, Optional, Union
from src.database.database import engine
from src.model.models import SitesModels
from bs4 import BeautifulSoup
from src.views.tags_view import list_tags
from datetime import datetime
import random
import json


def check_if_all_array_items_is_blank(arr):
    if not isinstance(arr, list):
        raise ValueError("Input must be a list")

    is_all_blank = all(element == "" for element in arr)
    return is_all_blank


def teste():

    search_url = f'https://docs.google.com/spreadsheets/d/1y_KpXEZSOsIu8LHfie5-Uon3VkG_PBew5hm_C63EDUQ/edit#gid=0'

    response = requests.get(search_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # for script in soup(['script']):
        #    script.extract()

        table = soup.find('table')

        if table:
            # Itere sobre as linhas da tabela
            for row in table.find_all('tr'):
                # Itere sobre as células de cada linha
                cells = row.find_all('td')
                content = []
                print("--------------------------------")
                for cell in cells:
                    content.append(cell.text)
                    # print(cell.text)
                if not check_if_all_array_items_is_blank(content):
                    print(content)
    else:
        print(response)


teste()
