from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.model.models import UsuariosModels
from src.database.database import Base, engine
from src.controller.bot_controller import router as bot_controllers
from src.controller.tags_controller import router as tags_controller
from src.controller.search_schedule_controller import (
    router as search_schedule_controller,
)
from src.controller.usuarios_controller import router as usuarios_controller
from src.controller.login_controller import router as login_router
from src.controller.vitimas_controller import router as vitimas_router
from src.controller.reference_sites_controller import router as reference_site_router
from src.controller.feriados_controller import router as feriados_router
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
import bcrypt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.views.search_schedule_views import list_agendamento_pesquisas
from src.views.sites_view import find_sites_with_keywords
from datetime import date, datetime
from src.views.historySearch_views import get_latest_history_search, createHistorySearch
from datetime import date, datetime

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

""" origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://172.16.17.254:3000",
    "http://172.16.17.254",
    "http://172.16.17.254:3000/",
] """

origins = ["https://www.monitorafeminicidio.com/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()

hour_job = os.getenv("HOUR_JOB")
minute_job = os.getenv("MINUTE_JOB")
city = os.getenv("CITY")

print("horários do job --------------->", hour_job, minute_job)


@scheduler.scheduled_job(
    "cron",
    day_of_week="*",
    hour=int(os.getenv("HOUR_JOB")),
    minute=int(os.getenv("MINUTE_JOB")),
)
async def execute_daily_task():
    print(
        "-------------------------iniciei o job diário-------------------------",
        datetime.now(),
    )
    await check_search()


async def check_search():
    current_day = date.today()
    last_search_date = None

    last_search = await get_latest_history_search()

    if last_search:
        created_at_str = last_search.createdAt
        if created_at_str.endswith("+00"):
            created_at_str = created_at_str[:-3] + "+0000"

        last_search_datetime = datetime.strptime(
            created_at_str, "%Y-%m-%d %H:%M:%S.%f%z"
        )
        last_search_date = last_search_datetime.date()

    tempo = await list_agendamento_pesquisas()
    tempo_agendado = tempo[0].dias if tempo else 1

    print("Intervalo configurado (dias):", tempo_agendado)
    print("Última pesquisa:", last_search_date)

    if not last_search_date:
        await createHistorySearch()
        await find_sites_with_keywords(tempo_agendado=tempo_agendado)
        print("--------------Pesquisa realizada (primeira execução)-------------------")
        return

    days_difference = (current_day - last_search_date).days
    print("Diferença de dias:", days_difference)

    if days_difference >= tempo_agendado:
        await createHistorySearch()
        await find_sites_with_keywords(tempo_agendado=tempo_agendado)
        print("--------------Pesquisa realizada-------------------")
    else:
        print("--------------Intervalo de tempo não atingido-------------------")


@app.on_event("startup")
async def create_initial_user():
    scheduler.start()
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    default_password = "monitorafeminicidio092"

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(default_password.encode("utf-8"), salt)
    decoded_password = hashed_password.decode("utf-8")

    existing_user = (
        db_session.query(UsuariosModels).filter_by(email="admin@mail.com").first()
    )

    if existing_user is None:
        db_user = UsuariosModels(
            nome="Administrador",
            email="admin@mail.com",
            telefone="99999999",
            senha=decoded_password,
            acesso=True,
            perfil="administrativo",
        )
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)


SECRET_KEY = "80zzm081sr@nd0m"
ALGORITHM = "HS256"
EXCLUDE_PATHS = ["/api/login", "/api/recuperarSenha/"]


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


app.include_router(bot_controllers, prefix="/api")
app.include_router(tags_controller, prefix="/api")
app.include_router(search_schedule_controller, prefix="/api")
app.include_router(usuarios_controller, prefix="/api")
app.include_router(vitimas_router, prefix="/api")
app.include_router(reference_site_router, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(feriados_router, prefix="/api")

PORT = int(os.getenv("PORT_BACKEND", 8001))
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        workers=1,
        host="0.0.0.0",
        reload=True,
        port=PORT,
        proxy_headers=True,  # This enables --proxy-headers
        forwarded_allow_ips="*",  # This enables --forwarded-allow-ips
    )
