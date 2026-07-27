import json
from schemas import ItemPedidoSchema


def test_order_routes_se_consigo_criar_pedido(client_user):
    response_access_token = client_user.post(
        "/auth/login-form", data={"username": "adm", "password": "adm"}
    )
    access_token = response_access_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    novo_pedido = client_user.post("/pedidos/criar", headers=headers, data={"id": 1})

    assert novo_pedido.status_code == 201
    assert int(novo_pedido.json()["id"]) == 1


def test_order_routes_se_não_consigo_criar_pedido(client_user):
    response_access_token = client_user.post(
        "/auth/login-form", data={"username": "adm", "password": "adm"}
    )
    refresh_token = response_access_token.json()["refresh_token"]
    headers = {"Authorization": f"Bearer {refresh_token}", "Accept": "application/json"}
    novo_pedido = client_user.post("/pedidos/criar", headers=headers, data={"id": 1})

    assert novo_pedido.status_code == 401


def test_order_routes_se_consigo_criar_item_pedido(client_order):
    response_access_token = client_order.post(
        "/auth/login-form", data={"username": "adm", "password": "adm"}
    )
    access_token = response_access_token.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    item_pedido = json.dumps(
        {"quantidade": 1, "sabor": "Sushi", "tamanho": "G", "preco_unitario": 80.0}
    )

    id_pedido = 1
    novo_item_pedido = client_order.post(
        f"/pedidos/{id_pedido}/adicionar-item", headers=headers, content=item_pedido
    )

    assert novo_item_pedido.status_code == 201
    assert int(novo_item_pedido.json()["pedido"]) == id_pedido


def test_order_routes_se_consigo_deletar_item_pedido(client_order_item):
    response_access_token = client_order_item.post(
        "/auth/login-form", data={"username": "adm", "password": "adm"}
    )

    access_token = response_access_token.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    for idx in range(4):
        idx += 1
        item_pedido = client_order_item.delete(
            f"/pedidos/{idx}/remover-item", headers=headers
        )

        assert item_pedido.status_code == 200
        assert len(item_pedido.json()["itens"]) == 0


def test_order_routes_se_consigo_finalizar_pedido(client_order):
    response_access_token = client_order.post(
        "/auth/login-form", data={"username": "adm", "password": "adm"}
    )

    access_token = response_access_token.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    for idx in range(4):
        idx += 1
        pedido = client_order.put(f"/pedidos/{idx}/finalizar", headers=headers)

        assert pedido.status_code == 200
        assert pedido.json()["pedido"]["status"] == "FINALIZADO"


def test_order_routes_se_consigo_cancelar_pedido(client_order):
    response_access_token = client_order.post(
        "/auth/login-form", data={"username": "adm", "password": "adm"}
    )

    access_token = response_access_token.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    for idx in range(4):
        idx += 1
        pedido = client_order.put(f"/pedidos/{idx}/cancelar", headers=headers)

        assert pedido.status_code == 200
        assert pedido.json()["pedido"]["status"] == "CANCELADO"


def test_order_routes_se_consigo_listar_pedidos(client_order):
    response_access_token = client_order.post(
        "/auth/login-form", data={"username": "adm", "password": "adm"}
    )

    access_token = response_access_token.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    pedido = client_order.get("/pedidos/listar", headers=headers)

    assert pedido.status_code == 200
    assert len(pedido.json()["pedidos"]) == 4


def test_order_routes_se_nao_consigo_listar_pedidos(client_order):
    response_access_token = client_order.post(
        "/auth/login-form", data={"username": "teste", "password": "teste"}
    )

    access_token = response_access_token.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    pedido = client_order.get("/pedidos/listar", headers=headers)

    assert pedido.status_code == 401


def test_order_routes_se_consigo_listar_pedido_do_usuario(client_order):
    response_access_token = client_order.post(
        "/auth/login-form", data={"username": "teste", "password": "teste"}
    )

    access_token = response_access_token.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    pedido = client_order.get("/pedidos/listar/pedido-usuario", headers=headers)

    assert pedido.status_code == 200
    assert len(pedido.json()["pedidos"]) == 2
