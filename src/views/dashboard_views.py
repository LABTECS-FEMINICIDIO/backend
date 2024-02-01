# from pydantic import BaseModel
# from sqlalchemy.orm import sessionmaker
# from src.database.database import engine
# from src.model.models import FeriadosModels, TagsModels


# async def get_data_dashboard_views():
#     db = sessionmaker(bind=engine)
#     db_session = db()
#     feriados = db_session.query(FeriadosModels).all()
#     db_session.close()
#     return feriados
