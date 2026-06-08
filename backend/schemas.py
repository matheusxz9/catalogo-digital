from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
 
class ImagemOut(BaseModel):
    id: int
    imagem_url: str
    ordem: int
    model_config = {"from_attributes": True}
 
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)
    preco: float = Field(..., gt=0)
    estoque: int = Field(0, ge=0)
    categoria: str = Field(..., min_length=1, max_length=100)
    purchasePrice: Optional[float] = Field(None, ge=0)
    profitMargin: Optional[float] = Field(None, ge=0)
    promocional: bool = False
    preco_promocional: Optional[float] = Field(None, ge=0)

class ProdutoUpdate(ProdutoBase):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)
    preco: Optional[float] = Field(None, gt=0)
    estoque: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = Field(None, min_length=1, max_length=100)
    ativo: Optional[bool] = None
    promocional: Optional[bool] = None
    preco_promocional: Optional[float] = Field(None, ge=0)
 
class ProdutoPublicOut(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    preco: float
    preco_promocional: Optional[float] = None
    promocional: bool = False
    estoque: int
    categoria: str
    visualizacoes: int = 0
    imagem_url: Optional[str] = None
    imagens: List[ImagemOut] = []
    ativo: bool
    criado_em: datetime
    model_config = {"from_attributes": True}

class ProdutoOut(ProdutoBase):
    id: int
    visualizacoes: int = 0
    imagem_url: Optional[str] = None
    imagens: List[ImagemOut] = []
    ativo: bool
    criado_em: datetime
    model_config = {"from_attributes": True}
 
class LoginInput(BaseModel):
    email: EmailStr
    senha: str
 
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
 
class AdminOut(BaseModel):
    id: int
    email: str
    ativo: bool
    model_config = {"from_attributes": True}
 
