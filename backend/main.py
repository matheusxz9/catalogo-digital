from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os
from pathlib import Path


load_dotenv()

# Run database migrations
import migrate
try:
    migrate.run_migration()
except Exception as e:
    print(f"Migration error: {e}")

from database import engine, Base, SessionLocal
import models
from auth import hash_senha
from routers import produtos, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Studio Bella Mizi - API")

_origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
origins = [o.strip() for o in _origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produtos.router)
app.include_router(admin.router)

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    def serve_frontend(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        index_path = FRONTEND_DIST / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"status": "ok", "mensagem": "API Studio Bella Mizi funcionando!"}
else:
    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    def root(full_path: str = ""):
        return {"status": "ok", "mensagem": "API Studio Bella Mizi funcionando!"}

def criar_admin_inicial():
    db: Session = SessionLocal()
    try:
        existe = db.query(models.Admin).first()
        if not existe:
            email = os.getenv("ADMIN_EMAIL", "admin@studiobellamizi.com")
            senha = os.getenv("ADMIN_SENHA")
            admin_obj = models.Admin(
                email=email,
                senha_hash=hash_senha(senha),
            )
            db.add(admin_obj)
            db.commit()
            print(f"Admin criado: {email}")
    finally:
        db.close()

criar_admin_inicial()