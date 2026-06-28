from fastapi import APIRouter
from services.usuario_service import CurrentUser
from services.pedido_service import PedidoService
from schemas import IdPedidoResponseSchema
from database import DBSession


order_routes = APIRouter(prefix="/order", tags=["Order Routes"])

@order_routes.post("/pedido", response_model=IdPedidoResponseSchema)
def criar_pedido(usuario: CurrentUser, db: DBSession):
    novo_pedido = PedidoService(db).criando_pedido(usuario.id)
    return IdPedidoResponseSchema.model_validate(novo_pedido)