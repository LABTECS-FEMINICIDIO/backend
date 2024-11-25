from os import environ
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

database_url= os.getenv("DATABASE_URL")
engine = create_engine(database_url)
Base = declarative_base()
