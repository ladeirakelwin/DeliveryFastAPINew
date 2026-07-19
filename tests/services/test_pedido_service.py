from src.services.pedido_service import PedidoService
from models import Pedido

VALID_USERS: list = [
    {"id": 1, "nome": "adm", "email": "adm@adm.com", "senha": "adm"},
    {"id": 2, "nome": "teste", "email": "teste@test.com", "senha": "teste"},
]
INVALID_USERS: list = [
    {"id": 3, "nome": "inativoa", "senha": "inativoa"},
    {"id": 4, "nome": "inativoa", "senha": "inativoa"},
    {"id": 5, "nome": "nonecxiste", "senha": "nonecxiste"},
]


def test_pedido_service_se_consigo_criar_pedido(user_seeded_db):
    pedido_service = PedidoService(user_seeded_db)
    for user in VALID_USERS:
        pedido = pedido_service.criando_pedido(user.get("id"))

        assert isinstance(pedido, Pedido)
