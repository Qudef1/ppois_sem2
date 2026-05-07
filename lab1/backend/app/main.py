from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import build_api_router

app = FastAPI(title="Theater Web UI", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(build_api_router())
