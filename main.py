from fastapi import FastAPI
from routers.health_router import router as health_router
from routers.chat_router import router as chat_router

app = FastAPI()

app.include_router(health_router)
app.include_router(chat_router)
