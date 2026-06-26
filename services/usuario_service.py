from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Usuario
from fastapi.exceptions import HTTPException
from fastapi import status
from utils.senha import validar_senha, criptografar_senha


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db

    def _obtendo_usuario(self, email: str) -> Usuario | None:
        usuario_db = select(Usuario).where(Usuario.email == email)
        usuario = self.db.scalar(usuario_db)
        return usuario

    def autenticar_usuario(self, email: str, senha: str) -> Usuario | None:
        usuario = self._obtendo_usuario(email)

        if not usuario and validar_senha(senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválido!",
            )

        return usuario

    def criar_usuario(
        self,
        email: str,
        senha: str,
        nome: str,
        ativo: bool = False,
        admin: bool = False,
    ):
        usuario = self._obtendo_usuario(email)
        if usuario:
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
                admin=admin,
            )

            self.db.add(novo_usuario)
            self.db.commit()

            return novo_usuario
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro inesperado!",
            )
