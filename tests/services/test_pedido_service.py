from src.services.pedido_service import PedidoService
from src.services.usuario_service import UsuarioService
from models import Pedido
from fastapi.exceptions import HTTPException
import pytest

VALID_USERS: list = [
    {"id": 1, "nome": "adm", "email": "adm@adm.com", "senha": "adm"},
    {"id": 2, "nome": "teste", "email": "teste@test.com", "senha": "teste"},
]
INVALID_USERS: list = [
    {"id": 3, "nome": "inativoa", "senha": "inativoa"},
    {"id": 4, "nome": "inativoa", "senha": "inativoa"},
    {"id": 5, "nome": "nonecxiste", "senha": "nonecxiste"},
]

ORDERS_ID = [1, 2]


def test_pedido_service_se_consigo_criar_pedido(user_seeded_db):
    pedido_service = PedidoService(user_seeded_db)
    for user in VALID_USERS:
        pedido = pedido_service.criando_pedido(
            user.get("id"), UsuarioService(user_seeded_db)
        )

        assert isinstance(pedido, Pedido)


def test_pedido_service_se_nao_consigo_criar_pedido_com_usuario_invalido(
    user_seeded_db,
):
    pedido_service = PedidoService(user_seeded_db)

    for invalid_user in INVALID_USERS:
        with pytest.raises(HTTPException) as exc:
            pedido_service.criando_pedido(
                invalid_user.get("id"), UsuarioService(user_seeded_db)
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Usuario não autorizado!"


def test_pedido_service_se_eh_tratado_error_inesperado_ao_criar_pedido(
    user_seeded_db,
):
    pedido_service = PedidoService(user_seeded_db)

    for invalid_user in INVALID_USERS:
        with pytest.raises(HTTPException) as exc:
            pedido_service.criando_pedido(invalid_user.get("id"), user_seeded_db)

        assert exc.value.status_code == 422
        assert (
            exc.value.detail
            == "Não foi possível criar o pedido, tente novamente mais tarde!"
        )


def test_pedido_service_se_consigo_alterar_status_pedido(order_seeded_db):
    pedido_service = PedidoService(order_seeded_db)
    usuario_service = UsuarioService(order_seeded_db)

    for id_pedido, user in enumerate(VALID_USERS):
        id_pedido += 1
        usuario = usuario_service.autenticar_usuario(
            user.get("nome"), user.get("senha")
        )
        pedido = pedido_service.alterar_status_pedido(id_pedido, "CANCELADO", usuario)
        assert pedido.status == "CANCELADO"
