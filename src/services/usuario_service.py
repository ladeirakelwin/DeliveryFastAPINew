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
from src.utils.exceptions import SQL_ERROR, start_detail_error
from src.utils.exceptions import USUARIO_INATIVO, EXCECAO_CREDENCIAL
from loguru import logger


class UsuarioService:
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

    def autenticar_usuario(self, email: str, senha: str) -> Usuario:
        usuario = self._obtendo_usuario_email(email)

        if not usuario or not validar_senha(senha, usuario.senha):
            logger.error("Erro ao autenticar com usuário ou senha inválido.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválido!",
            )

        if not usuario.ativo:
            raise USUARIO_INATIVO

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
            logger.error("Erro ao criar conta existente!")
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
        except (TypeError, Exception) as err:
            logger.exception("Erro ao alterar status pedido: ")
            self.db.rollback()
            if type(err) is TypeError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Senha e/ou nome de usuário e/ou email deve ser string!",
                )
            else:
                raise start_detail_error("Não foi possível criar usuário! ", SQL_ERROR)

    def obter_usuario_atual(self, token: str) -> Usuario:
        try:
            email = AuthService.decodificar_token(token).get("sub")
            tipo_token = AuthService.decodificar_token(token).get("type")
            if not email or tipo_token != "access":
                logger.error(
                    "Erro ao obter usuario atual com email ou tipo_token inválido!"
                )
                raise EXCECAO_CREDENCIAL

            usuario = self._obtendo_usuario_email(email)
            if not usuario:
                logger.error("Erro ao obter usuario atual com usuário inexistente!")
                raise EXCECAO_CREDENCIAL
            if not usuario.ativo:
                logger.error("Erro ao obter usuario atual com usuário inativo!")
                raise USUARIO_INATIVO

            return usuario

        except HTTPException as exc:
            logger.exception("Erro ao obter usuario atual: ")

            if exc.status_code == 401:
                raise EXCECAO_CREDENCIAL
            else:
                raise USUARIO_INATIVO
        except Exception as error:
            logger.exception("Erro ao obter usuario atual: ")
            raise error

    def obter_status_usuario(
        self, id: int = 0, email: str = "", nome: str = ""
    ) -> tuple[bool, bool]:
        resposta_padrao = (False, False)
        usuario = self._obtendo_usuario_id(id)
        if usuario:
            return (usuario.admin, usuario.ativo)

        usuario = self._obtendo_usuario_email(email)
        if usuario:
            return (usuario.admin, usuario.ativo)

        usuario = self._obtendo_usuario_nome(nome)
        if usuario:
            return (usuario.admin, usuario.ativo)

        return resposta_padrao


def obter_usuario_autenticado(
    db: DBSession, token: Annotated[str, Depends(oauth2_scheme)]
):
    return UsuarioService(db).obter_usuario_atual(token)


CurrentUser = Annotated[Usuario, Depends(obter_usuario_autenticado)]
