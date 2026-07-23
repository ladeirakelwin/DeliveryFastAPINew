from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas import (
    UsuarioResponseSchema,
    UsuarioCreate,
    TokenSchema,
    RefreshTokenSchema,
)
from src.services.usuario_service import UsuarioService
from src.services.auth_service import AuthService
from typing import Annotated
from database import DBSession


auth_routes = APIRouter(prefix="/auth", tags=["Auth Routes"])
AccessTokenLogin = Annotated[OAuth2PasswordRequestForm, Depends()]


@auth_routes.post("/criar-conta", response_model=UsuarioResponseSchema, status_code=201)
async def criar_conta(usuario: UsuarioCreate, db: DBSession):
    usuario_service = UsuarioService(db)
    novo_usuario = usuario_service.criar_usuario(
        usuario.email, usuario.senha, usuario.nome, usuario.ativo or True
    )

    return UsuarioResponseSchema.model_validate(novo_usuario)


@auth_routes.post("/login-form", response_model=TokenSchema, status_code=201)
async def autenticando_usuario(form_data: AccessTokenLogin, db: DBSession):
    usuario_service = UsuarioService(db)
    usuario = usuario_service.autenticar_usuario(form_data.username, form_data.password)

    access_token = AuthService().criar_token({"sub": usuario.nome})
    refresh_token = AuthService().criar_token({"sub": usuario.nome}, True)

    return TokenSchema(
        access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
    )


@auth_routes.post("/refresh", response_model=TokenSchema)
def obtendo_novos_token(payload: RefreshTokenSchema):
    access_token, refresh_token = AuthService().atualizar_token(payload.refresh_token)
    return TokenSchema(
        refresh_token=refresh_token, access_token=access_token, token_type="Bearer"
    )
