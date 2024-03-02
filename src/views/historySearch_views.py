from sqlalchemy.orm import sessionmaker
from src.database.database import engine
from src.model.models import HistorySearchModels
from sqlalchemy import desc

async def listAllHistorySearch():
    db = sessionmaker(bind=engine)
    db_session = db()

    histories = db_session.query(HistorySearchModels).all()
    db_session.close()
    return histories


async def createHistorySearch():
    historySearch = HistorySearchModels()
    db = sessionmaker(bind=engine)
    db_session.add(historySearch)
    db_session = db()
    return historySearch

async def get_latest_history_search():
    db_session = sessionmaker(bind=engine)
    latest_search = db_session.query(HistorySearchModels).order_by(desc(HistorySearchModels.createdAt)).first()
    db_session.close() 
    return latest_search