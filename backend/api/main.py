import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers.games import router

app = FastAPI(
    title="Belote Online API",
    version="0.1.0",
    description="REST API exposing a Python Belote game engine.",
)

# Local dev default: the Vite frontend runs on http://localhost:5173.
# Production single-service default: the frontend and API share the same origin,
# so CORS is not required unless CORS_ALLOWED_ORIGINS is configured.
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/health')
def health():
    return {'status': 'ok'}

app.include_router(router)

# Render deployment: the Dockerfile builds the Vite frontend into frontend/dist.
# If that folder exists, FastAPI also serves the React application.
frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
