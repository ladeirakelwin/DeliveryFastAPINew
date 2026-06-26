from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from schemas import UsuarioResponseSchema, UsuarioSchema
from services.usuario_service import UsuarioService
from database import DBSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth_routes = APIRouter(prefix="/auth", tags=["Auth Routes"])

@auth_routes.post("/criar-conta", response_model=UsuarioResponseSchema)
async def criar_conta(usuario: UsuarioSchema, db: DBSession ):
    usuario_service = UsuarioService(db)
    novo_usuario = usuario_service.criar_usuario(usuario.email, usuario.senha, usuario.nome, usuario.ativo, usuario.admin)

    return UsuarioResponseSchema.model_validate(novo_usuario)
