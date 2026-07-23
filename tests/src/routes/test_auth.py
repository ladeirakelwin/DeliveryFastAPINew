from httpx2 import Response


def test_auth_routes_se_consigo_criar_uma_conta(client):
    data = {
        "email": "teste2@teste2.com",
        "senha": "teste2",
        "nome": "teste2",
        "ativo": True,
    }
    response: Response = client.post("/auth/criar-conta", json=data)

    assert response.status_code == 201
    assert response.json()["nome"] == data.get("nome")


def test_auth_routes_se_nao_consigo_criar_uma_conta_existente(client):
    data = {
        "email": "teste2@teste2.com",
        "senha": "teste2",
        "nome": "teste2",
        "ativo": True,
    }
    client.post("/auth/criar-conta", json=data)
    response: Response = client.post("/auth/criar-conta", json=data)

    assert response.status_code == 409
    assert response.json()["detail"] == "Conta já existe!"
