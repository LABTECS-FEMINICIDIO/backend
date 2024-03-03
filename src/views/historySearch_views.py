from sqlalchemy.orm import sessionmaker
from src.database.database import engine
from src.model.models import HistorySearchModels
from sqlalchemy import desc
from fastapi.encoders import jsonable_encoder

async def listAllHistorySearch():
    db = sessionmaker(bind=engine)
    db_session = db()

    histories = db_session.query(HistorySearchModels).all()
    db_session.close()
    return histories


async def createHistorySearch():
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()
    db_history = HistorySearchModels()
    db_session.add(db_history)
    db_session.commit()
    db_session.refresh(db_history)
    print(jsonable_encoder(db_history))
    return jsonable_encoder(db_history)

    # db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # db_session = db()
    # db_vitima = VitimasModels(**vitima.model_dump())
    # db_session.add(db_vitima)
    # db_session.commit()
    # db_session.refresh(db_vitima)
    # return jsonable_encoder(db_vitima)

async def get_latest_history_search():
    db = sessionmaker(bind=engine)
    db_session = db()
    latest_search = db_session.query(HistorySearchModels).order_by(desc(HistorySearchModels.createdAt)).first()
    db_session.close() 
    return latest_search