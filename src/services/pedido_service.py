from models import Pedido, Usuario, ItensPedido
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from src.services.usuario_service import UsuarioService
from schemas import ItemPedidoSchema, PaginationSchema
from src.utils.exceptions import (
    start_detail_error,
    UNAUTHORIZED_USER,
    ORDER_ITEM_NOT_FOUNDED,
    ORDER_ITEM_WITH_ORDER_NOT_FOUNDED,
    ORDER_NOT_FOUNDED,
    ORDER_ERROR,
    ORDER_NOT_CREATED,
    SQL_ERROR,
)
from typing import Literal


class PedidoService:
    def __init__(self, db: Session):
        self.db = db

    def _calcular_total_pedido(self, pedido: Pedido) -> Pedido:
        pedido.preco = sum(
            [float(item.preco_unitario) * item.quantidade for item in pedido.itens]
        )
        try:
            self.db.commit()
            self.db.refresh(pedido)

            return pedido
        except Exception:
            self.db.rollback()

            raise

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

    def criando_pedido(
        self, id_usuario: int, usuario_service: UsuarioService
    ) -> Pedido:
        status_pedido: str = "PENDENTE"
        preco: int = 0
        try:
            _, usuario_ativo = usuario_service.obter_status_usuario(id=id_usuario)
            if not usuario_ativo:
                raise UNAUTHORIZED_USER

            novo_pedido = Pedido(id_usuario, status_pedido, preco)

            self.db.add(novo_pedido)
            self.db.commit()

            return novo_pedido

        except HTTPException:
            self.db.rollback()
            raise UNAUTHORIZED_USER

        except Exception:
            self.db.rollback()
            raise ORDER_NOT_CREATED

    def adicionando_item_pedido(
        self, id_pedido: int, usuario: Usuario, item_pedido: ItemPedidoSchema
    ) -> tuple[Pedido, ItensPedido]:
        try:
            pedido = self._obtendo_pedido(id_pedido)
        except Exception:
            raise ORDER_ERROR

        if not pedido:
            raise ORDER_NOT_FOUNDED

        if not usuario.admin and usuario.id != pedido.usuario:
            raise UNAUTHORIZED_USER

        novo_item_pedido = ItensPedido(
            quantidade=item_pedido.quantidade,
            sabor=item_pedido.sabor,
            tamanho=item_pedido.tamanho,
            preco_unitario=item_pedido.preco_unitario,
            pedido=pedido.id,
        )
        try:
            self.db.add(novo_item_pedido)
            self.db.commit()

            pedido_atualizado = self._calcular_total_pedido(pedido)

            return pedido_atualizado, novo_item_pedido
        except Exception:
            self.db.rollback()
            raise start_detail_error("Não foi pedido adicionar item pedido!", SQL_ERROR)

    def remover_item_pedido(self, id_item_pedido: int, usuario: Usuario) -> Pedido:
        item_pedido = self._obtendo_item_pedido(id_item_pedido)

        if not item_pedido:
            raise ORDER_ITEM_NOT_FOUNDED

        pedido_associado = self._obtendo_pedido(item_pedido.pedido)

        if not pedido_associado:
            raise ORDER_ITEM_WITH_ORDER_NOT_FOUNDED

        if not usuario.admin and usuario.id != pedido_associado.usuario:
            raise UNAUTHORIZED_USER

        try:
            self.db.delete(item_pedido)
            self.db.commit()

            pedido_associado_recalculado = self._calcular_total_pedido(pedido_associado)

            return pedido_associado_recalculado
        except Exception:
            self.db.rollback()
            raise start_detail_error(
                "Não foi possível remover item do pedido! ", SQL_ERROR
            )

    def alterar_status_pedido(
        self,
        id_pedido: int,
        novo_status: Literal["CANCELADO", "FINALIZADO"],
        usuario: Usuario,
    ):
        pedido = self._obtendo_pedido(id_pedido)
        if not pedido:
            raise ORDER_NOT_FOUNDED

        if not usuario.admin and usuario.id != pedido.usuario:
            raise UNAUTHORIZED_USER

        pedido.status = novo_status

        try:
            self.db.commit()
            self.db.refresh(pedido)

            return pedido
        except Exception:
            self.db.rollback()
            raise start_detail_error(
                "Não foi possível alterar status do pedido! ", SQL_ERROR
            )

    def listar_todos_pedidos(
        self, usuario: Usuario, query: PaginationSchema
    ) -> list[Pedido]:

        if not usuario.admin:
            raise UNAUTHORIZED_USER

        pedidos = self._obtendo_pedidos(query)

        return pedidos

    def listar_todos_pedidos_usuarios(self, usuario: Usuario) -> list[Pedido]:
        pedidos = self._obtendo_pedidos_usuario(usuario.id)
        return pedidos
