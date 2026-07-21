from src.services.pedido_service import PedidoService
from src.services.usuario_service import UsuarioService
from models import Pedido
from schemas import PaginationSchema
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

    for id_pedido, user in enumerate(VALID_USERS, start=1):
        usuario = usuario_service.autenticar_usuario(
            user.get("nome"), user.get("senha")
        )
        pedido = pedido_service.alterar_status_pedido(id_pedido, "CANCELADO", usuario)
        assert pedido.status == "CANCELADO"


def test_pedido_service_se_nao_consigo_alterar_status_pedido_inexistente(
    order_seeded_db,
):
    pedido_service = PedidoService(order_seeded_db)
    usuario_service = UsuarioService(order_seeded_db)

    usuario = usuario_service.autenticar_usuario(
        VALID_USERS[0].get("nome"), VALID_USERS[0].get("senha")
    )

    with pytest.raises(HTTPException) as exc:
        pedido_service.alterar_status_pedido(0, "CANCELADO", usuario)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Pedido não encontrado!"


def test_pedido_service_se_nao_consigo_alterar_status_pedido_sem_devidas_permissões(
    order_seeded_db,
):
    pedido_service = PedidoService(order_seeded_db)
    usuario_service = UsuarioService(order_seeded_db)

    usuario = usuario_service.autenticar_usuario(
        VALID_USERS[1].get("nome"), VALID_USERS[1].get("senha")
    )

    with pytest.raises(HTTPException) as exc:
        pedido_service.alterar_status_pedido(1, "CANCELADO", usuario)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Usuario não autorizado!"


def test_pedido_service_se_admin_consegue_listar_todos_pedidos(order_seeded_db):
    pedido_service = PedidoService(order_seeded_db)
    usuario_service = UsuarioService(order_seeded_db)

    admin = VALID_USERS[0]
    usuario = usuario_service.autenticar_usuario(admin.get("nome"), admin.get("senha"))
    pedidos = pedido_service.listar_todos_pedidos(
        usuario, PaginationSchema(offset=0, limit=50)
    )

    assert len(pedidos) == 4


def test_pedido_service_se_quem_nao_tem_admin_eh_proibido_de_listar_todos_pedido(
    order_seeded_db,
):
    pedido_service = PedidoService(order_seeded_db)
    usuario_service = UsuarioService(order_seeded_db)

    not_admin = VALID_USERS[1]

    usuario = usuario_service.autenticar_usuario(
        not_admin.get("nome"), not_admin.get("senha")
    )

    with pytest.raises(HTTPException) as exc:
        pedido_service.listar_todos_pedidos(
            usuario, PaginationSchema(offset=0, limit=50)
        )

    assert exc.value.detail == "Usuario não autorizado!"
    assert exc.value.status_code == 401


def test_pedido_service_se_consigo_listar_pedidos_de_um_usuario(order_seeded_db):
    pedido_service = PedidoService(order_seeded_db)
    usuario_service = UsuarioService(order_seeded_db)

    for users in VALID_USERS:
        usuario = usuario_service.autenticar_usuario(
            users.get("nome"), users.get("senha")
        )
        pedidos = pedido_service.listar_todos_pedidos_usuarios(usuario)

        assert len(pedidos) == 2


def test_pedido_service_se_consigo_remover_item_de_um_pedido(order_item_seeded_db):
    pedido_service = PedidoService(order_item_seeded_db)
    usuario_service = UsuarioService(order_item_seeded_db)

    for index, users in enumerate(VALID_USERS, start=1):
        usuario = usuario_service.autenticar_usuario(
            users.get("nome"), users.get("senha")
        )

        pedidos = pedido_service.remover_item_pedido(index, usuario)

        assert len(pedidos.itens) == 0


def test_pedido_service_se_consigo_remover_item_inexistente_de_um_pedido(
    order_item_without_order_seeded_db,
):
    pedido_service = PedidoService(order_item_without_order_seeded_db)
    usuario_service = UsuarioService(order_item_without_order_seeded_db)

    usuario = usuario_service.autenticar_usuario(
        VALID_USERS[0].get("nome"), VALID_USERS[0].get("senha")
    )
    with pytest.raises(HTTPException) as exc:
        pedido_service.remover_item_pedido(4, usuario)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Pedido associado ao item pedido não encontrado!"
