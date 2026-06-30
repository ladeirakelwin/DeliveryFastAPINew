from fastapi import APIRouter
from services.usuario_service import CurrentUser
from services.pedido_service import PedidoService
from schemas import (
    IdPedidoResponseSchema,
    ItemPedidoSchema,
    AdicionarItemPedidoResponseSchema,
    PedidoSchema,
    AlterarPedidoResponseSchema,
)
from database import DBSession


order_routes = APIRouter(prefix="/pedidos", tags=["Order Routes"])


@order_routes.post("/pedido", response_model=IdPedidoResponseSchema)
def criar_pedido(usuario: CurrentUser, db: DBSession):
    novo_pedido = PedidoService(db).criando_pedido(usuario.id)
    return IdPedidoResponseSchema.model_validate(novo_pedido)


@order_routes.post(
    "/pedido/adicionar-item/{id_pedido}",
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
    "/pedido/remover-item/{id_item_pedido}", response_model=PedidoSchema
)
def deletar_item_pedido(id_item_pedido: int, usuario: CurrentUser, db: DBSession):
    pedido = PedidoService(db).remover_item_pedido(id_item_pedido, usuario)

    return PedidoSchema.model_validate(pedido)


@order_routes.put(
    "/pedidos/pedido/finalizar/{id_pedido}",
    response_model=AlterarPedidoResponseSchema,
)
def finalizar_pedido(id_pedido: int, usuario: CurrentUser, db: DBSession):
    pedido = PedidoService(db).alterar_status_pedido(id_pedido, "FINALIZADO", usuario)

    return AlterarPedidoResponseSchema.model_validate(
        {"mensagem": "Pedido finalizado com sucesso!", "pedido": pedido}
    )
