from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(String(1000), nullable=True)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    categoria = Column(String(100), nullable=False)
    # Mantém a primeira imagem aqui para compatibilidade
    imagem_url = Column(String(500), nullable=True)
    imagem_public_id = Column(String(200), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    imagens = relationship("ProdutoImagem", back_populates="produto", cascade="all, delete-orphan", order_by="ProdutoImagem.ordem")

class ProdutoImagem(Base):
    __tablename__ = "produto_imagens"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    imagem_url = Column(String(500), nullable=False)
    imagem_public_id = Column(String(200), nullable=True)
    ordem = Column(Integer, default=0)

    produto = relationship("Produto", back_populates="imagens")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    senha_hash = Column(String(200), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())