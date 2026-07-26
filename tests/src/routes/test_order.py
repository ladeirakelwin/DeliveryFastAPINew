def test_order_routes_se_consigo_criar_pedido(client_user):
    response_access_token = client_user.post(
        "/auth/login-form", data={"username": "adm", "password": "adm"}
    )
    access_token = response_access_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    novo_pedido = client_user.post("/pedidos/criar", headers=headers, data={"id": 1})

    assert novo_pedido.status_code == 201
    assert int(novo_pedido.json()["id"]) == 1
