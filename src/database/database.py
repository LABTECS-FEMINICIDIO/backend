from os import environ
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# engine = create_engine("postgresql://postgres:teste-dean@24.199.108.245:5445/newDataTeste")
engine = create_engine(os.getenv("DATABASE_URL"))

Base = declarative_base()
