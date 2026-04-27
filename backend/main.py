from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os


load_dotenv()

from database import engine, Base, SessionLocal
import models
from auth import hash_senha
from routers import produtos, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Studio Bella Mizi - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produtos.router)
app.include_router(admin.router)

@app.get("/")
def root():
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
            print(f"Admin criado: {email} / senha: {senha}")
    finally:
        db.close()

criar_admin_inicial()