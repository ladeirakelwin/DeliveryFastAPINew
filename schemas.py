from pydantic import BaseModel, ConfigDict
from fastapi import Query
from typing import Optional


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]

class UsuarioBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str
    email: str
    ativo: Optional[bool]
    admin: Optional[bool]

class UsuarioSchema(UsuarioBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    
    senha: str

class UsuarioResponseSchema(UsuarioBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str 

class IdPedidoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class ItemPedidoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float

class ItemPedidoSchemaModel(ItemPedidoSchema):
    id: int
    pedido: int

class AdicionarItemPedidoResponseSchema(ItemPedidoSchema):
    pedido: int
    preco_pedido: float

class PedidoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    usuario: int
    preco: float
    itens: list[ItemPedidoSchemaModel]

class AlterarPedidoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mensagem: str
    pedido: PedidoSchema

class RefreshTokenSchema(BaseModel):
    refresh_token: str

class PaginationSchema(BaseModel):
    offset: int = Query(0, ge=0, description="Número de registro a pular")
    limit: int = Query(5, ge=1, le=50, description="Máximo de registros por página")


class ListarTodosPedidosResponseSchema(PaginationSchema):
    model_config = ConfigDict(from_attributes=True)
    
    pedidos: list[PedidoSchema]