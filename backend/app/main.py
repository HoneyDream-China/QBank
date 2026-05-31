import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import auth, banks, questions, progress, wrong, admin

app = FastAPI(title="刷题系统 API", version="1.0.0", redirect_slashes=False)

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(banks.router, prefix="/api/banks", tags=["题库"])
app.include_router(questions.router, prefix="/api/banks", tags=["题目"])
app.include_router(progress.router, prefix="/api/progress", tags=["进度"])
app.include_router(wrong.router, prefix="/api/wrong", tags=["错题"])
app.include_router(admin.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


# serve frontend static files in production
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
