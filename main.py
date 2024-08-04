from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.model.models import UsuariosModels
from src.database.database import Base, engine
from src.controller.bot_controller import router as bot_controllers
from src.controller.tags_controller import router as tags_controller
from src.controller.search_schedule_controller import router as search_schedule_controller
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
from jose import JWTError, jwt
from fastapi.responses import JSONResponse
from typing import Callable, List
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

origins = [
    "https://www.monitorafeminicidio.com/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("cron", day_of_week="*",  hour=23, minute=00)
async def execute_daily_task():
    await check_search()


# async def check_search():
#     tempo = await list_agendamento_pesquisas()
#     current_day = date.today()
#     last_search = await get_latest_history_search()
#     print(last_search["dias"])
    
#     if tempo:
#         tempo_agendado = tempo[0].dias
#     else:
#         tempo_agendado = 5

#     await find_sites_with_keywords(tempo_agendado=tempo_agendado)

async def check_search():
    current_day = date.today()
    last_search_date = ""
    last_search = await get_latest_history_search()
    
    if last_search:
        created_at_str = last_search.createdAt
        if created_at_str.endswith('+00'):
            created_at_str = created_at_str[:-3] + '+0000'
        last_search_datetime = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S.%f%z")
        last_search_date = last_search_datetime.date()
    
    tempo = await list_agendamento_pesquisas()

    if tempo:
        tempo_agendado = tempo[0].dias
    else:
        tempo_agendado = 1
    
    days_difference = None
    if last_search_date:
        days_difference = (current_day - last_search_date).days
        
    print("diferenca de dias", days_difference)
    print("last search", last_search_date)
    
    if days_difference:
        if days_difference >= (tempo_agendado - 1) or tempo_agendado == 1:
            await createHistorySearch()
            await find_sites_with_keywords(tempo_agendado=tempo_agendado)
            print("--------------Pesquisa realizada-------------------")
        else:
            print("--------------Intervalo de tempo não atingido-------------------")
    else:
        await createHistorySearch()
        await find_sites_with_keywords(tempo_agendado=tempo_agendado)
        print("--------------Pesquisa realizada-------------------")


    return 
    
@app.on_event("startup")
async def create_initial_user():
    scheduler.start()
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()

    default_password = "monitorafeminicidio092"

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), salt)
    decoded_password = hashed_password.decode('utf-8')

    existing_user = db_session.query(
        UsuariosModels).filter_by(email="admin@mail.com").first()

    if existing_user is None:
        db_user = UsuariosModels(
            nome="Administrador",
            email="admin@mail.com",
            telefone="99999999",
            senha=decoded_password,
            acesso=True,
            perfil="administrativo"
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

class JWTMiddleware:
    def __init__(self, app: FastAPI, secret_key: str, algorithm: str, exclude_paths: List[str] = None):
        self.app = app
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.exclude_paths = exclude_paths if exclude_paths else []

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope["type"] == "http" :
            request = Request(scope, receive)
            path = request.url.path

            if path in self.exclude_paths or request.method == "OPTIONS":
                await self.app(scope, receive, send)
                return

            token = request.headers.get("Authorization")
            if token:
                try:
                    if token.startswith("Bearer "):
                        token = token[len("Bearer "):]
                    else:
                        raise JWTError("Token inválido")

                    payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                    # request.state.user = payload
                except JWTError:
                    response = JSONResponse(status_code=401, content={"detail": "Token inválido"})
                    await response(scope, receive, send)
                    return
            else:
                response = JSONResponse(status_code=401, content={"detail": "Token não fornecido"})
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


app.add_middleware(JWTMiddleware, secret_key=SECRET_KEY, algorithm=ALGORITHM, exclude_paths=EXCLUDE_PATHS)

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
        reload=False,
        port=PORT,
        proxy_headers=True,  # This enables --proxy-headers
        forwarded_allow_ips="*",  # This enables --forwarded-allow-ips
    )
