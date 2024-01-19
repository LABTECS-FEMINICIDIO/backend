from fastapi import FastAPI
import uvicorn
from src.database.database import Base, engine
from src.controller.bot_controller import router as bot_controllers
from src.controller.tags_controller import router as tags_controller
from src.controller.search_schedule_controller import router as search_schedule_controller
from src.controller.usuarios_controller import router as usuarios_controller
from src.controller.login_controller import router as login_router
from src.controller.vitimas_controller import router as vitimas_router
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bot_controllers, prefix="/api")
app.include_router(tags_controller, prefix="/api")
app.include_router(search_schedule_controller, prefix="/api")
app.include_router(usuarios_controller, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(vitimas_router, prefix="/api")

PORT = int(os.getenv("PORT_BACKEND", 8000))
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        workers=1,
        host="0.0.0.0",
        reload=False,
        port=PORT
    )
