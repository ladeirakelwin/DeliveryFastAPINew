from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Usuario
from fastapi.exceptions import HTTPException
from fastapi import status, Depends
from src.utils.senha import validar_senha, criptografar_senha
from typing import Annotated
from database import DBSession
from dependencies import oauth2_scheme
from src.services.auth_service import AuthService


class UsuarioService:
    USUARIO_INATIVO = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo!"
    )
    EXCECAO_CREDENCIAL = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar credencial",
        headers={"WWW-Authenticate": "Bearer"},
    )

    def __init__(self, db: Session):
        self.db = db

    def _obtendo_usuario_nome(self, nome: str) -> Usuario | None:
        usuario_db = select(Usuario).where(Usuario.nome == nome)
        usuario = self.db.scalar(usuario_db)
        return usuario

    def _obtendo_usuario_email(self, email: str) -> Usuario | None:
        usuario_db = select(Usuario).where(Usuario.email == email)
        usuario = self.db.scalar(usuario_db)
        return usuario

    def _obtendo_usuario_id(self, id: int) -> Usuario | None:
        usuario_db = select(Usuario).where(Usuario.id == id)
        usuario = self.db.scalar(usuario_db)
        return usuario

    def autenticar_usuario(self, apelido: str, senha: str) -> Usuario:
        usuario = self._obtendo_usuario_nome(apelido)

        if not usuario or not validar_senha(senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválido!",
            )

        if not usuario.ativo:
            raise self.USUARIO_INATIVO

        return usuario

    def criar_usuario(
        self,
        email: str,
        senha: str,
        nome: str,
        ativo: bool = False,
    ):
        email_existe = self._obtendo_usuario_email(email)
        nome_existe = self._obtendo_usuario_nome(nome)

        if email_existe or nome_existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Conta já existe!"
            )
        try:
            senha_criptografada = criptografar_senha(senha)
            novo_usuario = Usuario(
                email=email,
                senha=senha_criptografada,
                nome=nome,
                ativo=ativo,
                admin=False,
            )

            self.db.add(novo_usuario)
            self.db.commit()

            return novo_usuario
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro inesperado!",
            )

    def obter_usuario_atual(self, token: str) -> Usuario:
        try:
            nome = AuthService.decodificar_token(token).get("sub")
            tipo_token = AuthService.decodificar_token(token).get("type")
            if not nome or tipo_token != "access":
                raise self.EXCECAO_CREDENCIAL

            usuario = self._obtendo_usuario_nome(nome)
            if not usuario:
                raise self.EXCECAO_CREDENCIAL
            if not usuario.ativo:
                raise self.USUARIO_INATIVO

            return usuario

        except HTTPException as exc:
            if exc.status_code == 401:
                raise self.EXCECAO_CREDENCIAL
            else:
                raise self.USUARIO_INATIVO
        except Exception as error:
            raise error


def obter_usuario_autenticado(
    db: DBSession, token: Annotated[str, Depends(oauth2_scheme)]
):
    return UsuarioService(db).obter_usuario_atual(token)


CurrentUser = Annotated[Usuario, Depends(obter_usuario_autenticado)]
