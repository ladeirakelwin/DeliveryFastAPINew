from database import Base
from sqlalchemy import ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.orm import mapped_column, Mapped, relationship


class Usuario(Base):
    __tablename__ = "Usuarios"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    nome: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(String)
    ativo: Mapped[bool] = mapped_column(Boolean)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


class Pedido(Base):
    __tablename__ = "Pedidos"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String)
    usuario: Mapped[int] = mapped_column(Integer, ForeignKey("Usuarios.id"))
    preco: Mapped[float] = mapped_column(Float)
    itens: Mapped[list["ItensPedido"]] = relationship(
        back_populates="pedido_relationship", cascade="all, delete-orphan"
    )

    def __init__(self, usuario, status="PENDENTE", preco=0):
        self.usuario = usuario
        self.status = status
        self.preco = preco


class ItensPedido(Base):
    __tablename__ = "ItensPedidos"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    quantidade: Mapped[int] = mapped_column(String)
    sabor: Mapped[str] = mapped_column(String)
    tamanho: Mapped[str] = mapped_column(String)
    preco_unitario: Mapped[float] = mapped_column(Float)
    pedido: Mapped[int] = mapped_column(Integer, ForeignKey("Pedidos.id"))

    pedido_relationship: Mapped["Pedido"] = relationship(back_populates="itens")

    def __init__(self, quantidade, sabor, tamanho, preco_unitario, pedido):
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido
