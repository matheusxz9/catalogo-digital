from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth import get_admin_atual
import models, schemas, cloudinary_service
import uuid

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.get("/", response_model=List[schemas.ProdutoOut])
def listar_produtos(db: Session = Depends(get_db)):
    return (
        db.query(models.Produto)
        .filter(models.Produto.ativo == True)
        .order_by(models.Produto.criado_em.desc())
        .all()
    )

@router.get("/{id}", response_model=schemas.ProdutoOut)
def buscar_produto(id: int, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).filter(
        models.Produto.id == id,
        models.Produto.ativo == True,
    ).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@router.post("/", response_model=schemas.ProdutoOut, status_code=201)
async def criar_produto(
    nome: str = Form(...),
    descricao: Optional[str] = Form(None),
    preco: float = Form(...),
    estoque: int = Form(0),
    categoria: str = Form(...),
    imagem: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_admin_atual),
):
    imagem_url = None
    imagem_public_id = None

    if imagem:
        conteudo = await imagem.read()
        nome_arquivo = f"produto_{uuid.uuid4().hex[:8]}"
        resultado = cloudinary_service.upload_imagem(conteudo, nome_arquivo)
        imagem_url = resultado["url"]
        imagem_public_id = resultado["public_id"]

    produto = models.Produto(
        nome=nome,
        descricao=descricao,
        preco=preco,
        estoque=estoque,
        categoria=categoria,
        imagem_url=imagem_url,
        imagem_public_id=imagem_public_id,
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto

@router.put("/{id}", response_model=schemas.ProdutoOut)
def atualizar_produto(
    id: int,
    dados: schemas.ProdutoUpdate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_admin_atual),
):
    produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto

@router.post("/{id}/imagem", response_model=schemas.ProdutoOut)
async def atualizar_imagem(
    id: int,
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_admin_atual),
):
    produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if produto.imagem_public_id:
        cloudinary_service.deletar_imagem(produto.imagem_public_id)

    conteudo = await imagem.read()
    nome_arquivo = f"produto_{id}_{uuid.uuid4().hex[:8]}"
    resultado = cloudinary_service.upload_imagem(conteudo, nome_arquivo)

    produto.imagem_url = resultado["url"]
    produto.imagem_public_id = resultado["public_id"]
    db.commit()
    db.refresh(produto)
    return produto

@router.delete("/{id}", status_code=204)
def deletar_produto(
    id: int,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_admin_atual),
):
    produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.ativo = False
    db.commit()