from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import verificar_senha, criar_token, get_admin_atual
import models, schemas
import uuid
from typing import List

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

@router.get("/produtos", response_model=List[schemas.ProdutoOut])
def listar_produtos_admin(db: Session = Depends(get_db), _: models.Admin = Depends(get_admin_atual)):
    return db.query(models.Produto).order_by(models.Produto.criado_em.desc()).all()

@router.post("/produtos/{id}/duplicar", response_model=schemas.ProdutoOut, status_code=201)
def duplicar_produto(id: int, db: Session = Depends(get_db), _: models.Admin = Depends(get_admin_atual)):
    original = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    novo = models.Produto(
        nome=f"{original.nome} (cópia)",
        descricao=original.descricao,
        preco=original.preco,
        estoque=0,
        categoria=original.categoria,
        purchasePrice=original.purchasePrice,
        profitMargin=original.profitMargin,
    )
    db.add(novo)
    db.flush()
    if original.imagens:
        import cloudinary_service
        for img in original.imagens:
            import httpx
            try:
                resp = httpx.get(img.imagem_url, timeout=10)
                if resp.status_code == 200:
                    r = cloudinary_service.upload_imagem(
                        resp.content, f"produto_{novo.id}_{uuid.uuid4().hex[:8]}"
                    )
                    db.add(models.ProdutoImagem(
                        produto_id=novo.id,
                        imagem_url=r["url"],
                        imagem_public_id=r["public_id"],
                        ordem=img.ordem,
                    ))
                    if img.ordem == 0:
                        novo.imagem_url = r["url"]
                        novo.imagem_public_id = r["public_id"]
            except Exception:
                pass
    db.commit()
    db.refresh(novo)
    return novo

@router.patch("/produtos/{id}/toggle-ativo", response_model=schemas.ProdutoOut)
def toggle_ativo(id: int, db: Session = Depends(get_db), _: models.Admin = Depends(get_admin_atual)):
    produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto.ativo = not produto.ativo
    db.commit()
    db.refresh(produto)
    return produto

@router.patch("/produtos/{id}/toggle-promocional", response_model=schemas.ProdutoOut)
def toggle_promocional(id: int, db: Session = Depends(get_db), _: models.Admin = Depends(get_admin_atual)):
    produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto.promocional = not produto.promocional
    if not produto.promocional:
        produto.preco_promocional = None
    db.commit()
    db.refresh(produto)
    return produto