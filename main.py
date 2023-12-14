from fastapi import FastAPI
import uvicorn
from src.database.database import Base, engine
from src.controller.bot_controller import router as bot_controllers
from src.controller.tags_controller import router as tags_controller
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

PORT = int(os.getenv("PORT_BACKEND", 8000))
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        workers=1,
        host="0.0.0.0",
        reload=True,
        port=PORT
    )
