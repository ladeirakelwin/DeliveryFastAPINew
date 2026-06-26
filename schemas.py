from pydantic import BaseModel, ConfigDict
from typing import Optional


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

class LoginSchema(BaseModel):
    username: str
    password: str