from fastapi import FastAPI
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
    "http://localhost",
    "http://localhost:3000",
    "http://192.168.1.109:3000",
    "http://192.168.1.109",
    "http://192.168.1.109:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("cron", day_of_week="*",  hour=23, minute=40)
async def execute_daily_task():
    check_search()


async def check_search():
    tempo = await list_agendamento_pesquisas()
    current_day = date.today()
    last_search = await get_latest_history_search()
    print(last_search["dias"])
    
    if tempo:
        tempo_agendado = tempo[0].dias
    else:
        tempo_agendado = 5

    await find_sites_with_keywords(tempo_agendado=tempo_agendado)

async def check_search():
    current_day = date.today()
    
    last_search = await get_latest_history_search()
    last_search_datetime = datetime.fromisoformat(last_search.createdAt)
    last_search_date = last_search_datetime.date()
    
    
    tempo = await list_agendamento_pesquisas()
    if tempo:
        tempo_agendado = tempo[0].dias
    else:
        tempo_agendado = 5
    
    days_difference = (current_day - last_search_date).days
    
    print(days_difference, tempo_agendado)

    if days_difference >= tempo_agendado:
        await find_sites_with_keywords(tempo_agendado=tempo_agendado)
        await createHistorySearch()
        print("--------------Pesquisa realizada-------------------")
    else:
        print("--------------Intervalo de tempo não atingido-------------------")

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

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     try:
#         start_time = time.time()
#         response = await call_next(request)
#         process_time = time.time() - start_time
#         response.headers["X-Process-Time"] = str(process_time)

#         authorization_header = request.headers.get("authorization", "")

#         if (request.url.path == "/api/login"):
#             return response
#         if (request.url.path == "/api/login/"):
#             return response

#         if authorization_header == "":
#             raise HTTPException(
#                 status_code=401,  detail="Credenciais inválidas.")

#         if "Bearer" in authorization_header:
#             token = authorization_header.split("Bearer")[1].strip()

#             decoded_token = jwt.decode(token, os.getenv(
#                 "SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
#             print((decoded_token["sub"]))
#             teste = decoded_token["sub"].replace("'", "\"")
#             print(json.loads(teste))

#             if token == "":
#                 raise HTTPException(
#                     status_code=401,  detail="Credenciais inválidas.")

#         return response
#     except Exception as e:
#         print(e)
#         return JSONResponse(status_code=401, content={'detail': "Token inválido."})

# def decode_token(token: str = Header(..., description="Token")):
#     credentials_exception = HTTPException(
#         status_code=401, detail="Token inválido"
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub").get("email")
#         if email is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     return payload

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
        port=PORT
    )
