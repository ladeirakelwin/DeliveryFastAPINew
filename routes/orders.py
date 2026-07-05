from fastapi import APIRouter, Depends
from services.usuario_service import CurrentUser
from services.pedido_service import PedidoService
from schemas import (
    IdPedidoResponseSchema,
    ItemPedidoSchema,
    AdicionarItemPedidoResponseSchema,
    PedidoSchema,
    AlterarPedidoResponseSchema,
    ListarTodosPedidosResponseSchema,
    PaginationSchema
)
from database import DBSession
from typing import Annotated

order_routes = APIRouter(prefix="/pedidos", tags=["Order Routes"])


@order_routes.post("/criar", response_model=IdPedidoResponseSchema)
def criar_pedido(usuario: CurrentUser, db: DBSession):
    novo_pedido = PedidoService(db).criando_pedido(usuario.id)
    return IdPedidoResponseSchema.model_validate(novo_pedido)


@order_routes.post(
    "/{id_pedido}/adicionar-item",
    response_model=AdicionarItemPedidoResponseSchema,
)
def adicionar_item_pedido(
    id_pedido: int, usuario: CurrentUser, db: DBSession, item_pedido: ItemPedidoSchema
):
    pedido, novo_item_pedido = PedidoService(db).adicionando_item_pedido(
        id_pedido, usuario, item_pedido
    )
    return AdicionarItemPedidoResponseSchema(
        quantidade=novo_item_pedido.quantidade,
        sabor=novo_item_pedido.sabor,
        tamanho=novo_item_pedido.tamanho,
        preco_unitario=novo_item_pedido.preco_unitario,
        pedido=pedido.id,
        preco_pedido=pedido.preco,
    )


@order_routes.delete(
    "/{id_item_pedido}/remover-item/", response_model=PedidoSchema
)
def deletar_item_pedido(id_item_pedido: int, usuario: CurrentUser, db: DBSession):
    pedido = PedidoService(db).remover_item_pedido(id_item_pedido, usuario)

    return PedidoSchema.model_validate(pedido)


@order_routes.put(
    "/{id_pedido}/finalizar/",
    response_model=AlterarPedidoResponseSchema,
)
def finalizar_pedido(id_pedido: int, usuario: CurrentUser, db: DBSession):
    pedido = PedidoService(db).alterar_status_pedido(id_pedido, "FINALIZADO", usuario)

    return AlterarPedidoResponseSchema.model_validate(
        {"mensagem": "Pedido finalizado com sucesso!", "pedido": pedido}
    )


@order_routes.put(
    "/{id_pedido}/cancelar/", response_model=AlterarPedidoResponseSchema
)
def cancelar_pedido(id_pedido: int, usuario: CurrentUser, db: DBSession):
    pedido = PedidoService(db).alterar_status_pedido(id_pedido, "CANCELADO", usuario)

    return AlterarPedidoResponseSchema.model_validate(
        {"mensagem": "Pedido cancelado com sucesso!", "pedido": pedido}
    )


@order_routes.get("/listar", response_model=ListarTodosPedidosResponseSchema)
def listar_pedidos(query: Annotated[PaginationSchema, Depends()], usuario: CurrentUser, db: DBSession ):
    pedidos = PedidoService(db).listar_todos_pedidos(usuario, query)
    return ListarTodosPedidosResponseSchema.model_validate({"offset": query.offset,"limit": query.limit,"pedidos": pedidos})


@order_routes.get("/listar/pedido-usuario/", response_model=ListarTodosPedidosResponseSchema)
def listar_pedidos_usuarios(usuario: CurrentUser, db: DBSession):
    pedidos = PedidoService(db).listar_todos_pedidos_usuarios(usuario)
    return ListarTodosPedidosResponseSchema.model_validate({"pedidos": pedidos})