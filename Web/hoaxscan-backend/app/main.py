import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, submissions

from app.config import settings
from app.routers import health
from app.services.llm_check import cek_gemini

# Tanpa ini, log INFO dari app (misalnya keputusan gerbang di analyzer) tidak tampil
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    cek_gemini()  # sekali saat startup, tidak pernah melempar error
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")