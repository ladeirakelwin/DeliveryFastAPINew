from database import Base
from sqlalchemy import ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.orm import mapped_column, Mapped, relationship

class Usuario(Base):
    __tablename__ = "Usuarios"

    id: Mapped[int] = mapped_column("id",Integer,primary_key=True, autoincrement=True,nullable=False)
    nome: Mapped[str] = mapped_column("nome", String)
    email: Mapped[str] = mapped_column("email", String, nullable=False)
    senha: Mapped[str] = mapped_column("senha", String)
    ativo: Mapped[bool] = mapped_column("ativo", Boolean)
    admin: Mapped[bool] = mapped_column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

class Pedido(Base):
    __tablename__ = "Pedidos"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    status: Mapped[str] = mapped_column("status", String)
    usuario: Mapped[int] = mapped_column("usuario",ForeignKey("Usuarios.id"))
    preco: Mapped[float] = mapped_column("preco", Float)
    itens = relationship("ItensPedido", cascade="all, delete")

    def __init__(self, usuario, status="PENDENTE", preco=0):
        self.usuario = usuario
        self.status = status
        self.preco = preco

class ItensPedido(Base):
    __tablename__ = "ItensPedidos"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    quantidade: Mapped[int] = mapped_column("quantidade", String)
    sabor: Mapped[str] = mapped_column("sabor", String)
    tamanho: Mapped[str] = mapped_column("tamanho", String)
    preco_unitario: Mapped[float] = mapped_column("preco_unitario", Float)
    pedido: Mapped[int] = relationship("Pedido",ForeignKey("Pedidos.id"))








