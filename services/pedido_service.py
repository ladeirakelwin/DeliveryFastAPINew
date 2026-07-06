from models import Pedido, Usuario, ItensPedido
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from fastapi import status
from schemas import ItemPedidoSchema, PaginationSchema
from typing import Literal


class PedidoService:
    PEDIDO_NAO_ENCONTRADO = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado!"
    )
    USUARIO_NAO_AUTORIZADO = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario não autorizado!"
    )

    def __init__(self, db: Session):
        self.db = db

    def _calcular_total_pedido(self, pedido: Pedido) -> Pedido:
        pedido.preco = sum(
            [float(item.preco_unitario) * int(item.quantidade) for item in pedido.itens]
        )

        self.db.commit()
        self.db.refresh(pedido)

        return pedido

    def _obtendo_pedido(self, id_pedido: int) -> Pedido | None:
        pedido_db = select(Pedido).where(Pedido.id == id_pedido)
        pedido = self.db.scalar(pedido_db)
        return pedido

    def _obtendo_pedidos(self, query: PaginationSchema) -> list[Pedido]:
        pedidos_db = select(Pedido).offset(query.offset).limit(query.limit)
        pedidos = list(self.db.scalars(pedidos_db).fetchall())
        return pedidos

    def _obtendo_pedidos_usuario(self, id_usuario: int) -> list[Pedido]:
        pedidos_db = select(Pedido).where(Pedido.usuario == id_usuario)
        pedidos = list(self.db.scalars(pedidos_db).fetchall())
        return pedidos

    def _obtendo_item_pedido(self, id_item_pedido: int) -> ItensPedido | None:
        item_pedido_db = select(ItensPedido).where(ItensPedido.id == id_item_pedido)
        item_pedido = self.db.scalar(item_pedido_db)
        return item_pedido

    def criando_pedido(self, id_usuario: int) -> Pedido:
        status_pedido: str = "PENDENTE"
        preco: int = 0
        try:
            novo_pedido = Pedido(id_usuario, status_pedido, preco)

            self.db.add(novo_pedido)
            self.db.commit()

            return novo_pedido
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Não foi possível criar o pedido, tente novamente mais tarde!",
            )

    def adicionando_item_pedido(
        self, id_pedido: int, usuario: Usuario, item_pedido: ItemPedidoSchema
    ) -> tuple[Pedido, ItensPedido]:
        try:
            pedido = self._obtendo_pedido(id_pedido)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao buscar pedido! Tente novamente mais tarde.",
            )
        if not pedido:
            raise self.PEDIDO_NAO_ENCONTRADO

        if not usuario.admin and usuario.id != pedido.usuario:
            raise self.USUARIO_NAO_AUTORIZADO

        novo_item_pedido = ItensPedido(
            quantidade=item_pedido.quantidade,
            sabor=item_pedido.sabor,
            tamanho=item_pedido.tamanho,
            preco_unitario=item_pedido.preco_unitario,
            pedido=pedido.id,
        )

        self.db.add(novo_item_pedido)
        self.db.commit()

        pedido_atualizado = self._calcular_total_pedido(pedido)

        return pedido_atualizado, novo_item_pedido

    def remover_item_pedido(self, id_item_pedido: int, usuario: Usuario) -> Pedido:
        item_pedido = self._obtendo_item_pedido(id_item_pedido)

        if not item_pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item pedido não encontrado!",
            )

        pedido_associado = self._obtendo_pedido(item_pedido.pedido)

        if not pedido_associado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido associado ao item pedido não encontrado!",
            )

        if not usuario.admin and usuario.id != pedido_associado.usuario:
            raise self.USUARIO_NAO_AUTORIZADO

        self.db.delete(item_pedido)
        self.db.commit()

        pedido_associado_recalculado = self._calcular_total_pedido(pedido_associado)

        return pedido_associado_recalculado

    def alterar_status_pedido(
        self,
        id_pedido: int,
        novo_status: Literal["CANCELADO", "FINALIZADO"],
        usuario: Usuario,
    ):
        pedido = self._obtendo_pedido(id_pedido)
        if not pedido:
            raise self.PEDIDO_NAO_ENCONTRADO

        if not usuario.admin and usuario.id != pedido.usuario:
            raise self.USUARIO_NAO_AUTORIZADO

        pedido.status = novo_status
        self.db.commit()
        self.db.refresh(pedido)

        return pedido

    def listar_todos_pedidos(
        self, usuario: Usuario, query: PaginationSchema
    ) -> list[Pedido]:

        if not usuario.admin:
            raise self.USUARIO_NAO_AUTORIZADO

        pedidos = self._obtendo_pedidos(query)

        return pedidos

    def listar_todos_pedidos_usuarios(self, usuario: Usuario) -> list[Pedido]:
        pedidos = self._obtendo_pedidos_usuario(usuario.id)
        return pedidos
