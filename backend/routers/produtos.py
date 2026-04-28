from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth import get_admin_atual
import models, schemas, cloudinary_service
import uuid
 
router = APIRouter(prefix="/produtos", tags=["Produtos"])
 
TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
TAMANHO_MAXIMO_BYTES = 5 * 1024 * 1024
MAX_IMAGENS = 4
 
def _validar_imagem(imagem: UploadFile, conteudo: bytes) -> None:
    if imagem.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail="Tipo não permitido. Use: jpeg, png ou webp")
    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo: 5MB")
 
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
    imagens: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_admin_atual),
):
    produto = models.Produto(
        nome=nome, descricao=descricao, preco=preco,
        estoque=estoque, categoria=categoria,
    )
    db.add(produto)
    db.flush()
 
    if imagens:
        validas = [img for img in imagens if img.filename][:MAX_IMAGENS]
        for ordem, imagem in enumerate(validas):
            conteudo = await imagem.read()
            if not conteudo:
                continue
            _validar_imagem(imagem, conteudo)
            resultado = cloudinary_service.upload_imagem(
                conteudo, f"produto_{produto.id}_{uuid.uuid4().hex[:8]}"
            )
            if ordem == 0:
                produto.imagem_url = resultado["url"]
                produto.imagem_public_id = resultado["public_id"]
            db.add(models.ProdutoImagem(
                produto_id=produto.id,
                imagem_url=resultado["url"],
                imagem_public_id=resultado["public_id"],
                ordem=ordem,
            ))
 
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
 
@router.post("/{id}/imagens", response_model=schemas.ProdutoOut)
async def adicionar_imagens(
    id: int,
    imagens: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_admin_atual),
):
    produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
 
    atuais = len(produto.imagens)
    espacos = MAX_IMAGENS - atuais
    if espacos <= 0:
        raise HTTPException(status_code=400, detail=f"Produto já tem {MAX_IMAGENS} imagens")
 
    validas = [img for img in imagens if img.filename][:espacos]
    for i, imagem in enumerate(validas):
        conteudo = await imagem.read()
        if not conteudo:
            continue
        _validar_imagem(imagem, conteudo)
        resultado = cloudinary_service.upload_imagem(
            conteudo, f"produto_{id}_{uuid.uuid4().hex[:8]}"
        )
        ordem = atuais + i
        db.add(models.ProdutoImagem(
            produto_id=id,
            imagem_url=resultado["url"],
            imagem_public_id=resultado["public_id"],
            ordem=ordem,
        ))
        if ordem == 0 or not produto.imagem_url:
            produto.imagem_url = resultado["url"]
            produto.imagem_public_id = resultado["public_id"]
 
    db.commit()
    db.refresh(produto)
    return produto
 
@router.delete("/{id}/imagens/{imagem_id}", response_model=schemas.ProdutoOut)
def deletar_imagem(
    id: int,
    imagem_id: int,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_admin_atual),
):
    imagem = db.query(models.ProdutoImagem).filter(
        models.ProdutoImagem.id == imagem_id,
        models.ProdutoImagem.produto_id == id,
    ).first()
    if not imagem:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
 
    if imagem.imagem_public_id:
        cloudinary_service.deletar_imagem(imagem.imagem_public_id)
    db.delete(imagem)
 
    produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    for i, img in enumerate(sorted(produto.imagens, key=lambda x: x.ordem)):
        img.ordem = i
 
    if produto.imagens:
        primeira = min(produto.imagens, key=lambda x: x.ordem)
        produto.imagem_url = primeira.imagem_url
        produto.imagem_public_id = primeira.imagem_public_id
    else:
        produto.imagem_url = None
        produto.imagem_public_id = None
 
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
    for img in produto.imagens:
        if img.imagem_public_id:
            cloudinary_service.deletar_imagem(img.imagem_public_id)
    produto.ativo = False
    db.commit()
 
