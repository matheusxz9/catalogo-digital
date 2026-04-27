from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import verificar_senha, criar_token, get_admin_atual
import models, schemas

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/login", response_model=schemas.TokenOut)
def login(dados: schemas.LoginInput, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == dados.email).first()

    if not admin or not verificar_senha(dados.senha, admin.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    if not admin.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )

    token = criar_token({"sub": admin.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.AdminOut)
def me(admin: models.Admin = Depends(get_admin_atual)):
    return admin