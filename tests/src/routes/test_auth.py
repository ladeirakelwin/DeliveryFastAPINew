from httpx2 import Response
import json


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


def test_auth_routes_se_consigo_obter_token(client_user):
    data = {
        "password": "teste",
        "username": "teste",
    }

    response: Response = client_user.post("/auth/login-form", data=data)

    assert response.status_code == 201
    assert response.json().get("refresh_token") is not None
    assert response.json().get("access_token") is not None


def test_auth_routes_se_nao_consigo_obter_token_com_usuario_invalido(client_user):
    data = {
        "password": "teste1",
        "username": "teste2",
    }

    response: Response = client_user.post("/auth/login-form", data=data)

    assert response.status_code == 401


def test_auth_routes_se_nao_consigo_obter_token_com_usuario_inativo(client_user):
    data = {
        "password": "inativoa",
        "username": "inativoa",
    }

    response: Response = client_user.post("/auth/login-form", data=data)

    assert response.status_code == 403


def test_auth_routes_se_consigo_obter_novos_tokens(client_user):
    data = {
        "password": "adm",
        "username": "adm",
    }

    response_auth: Response = client_user.post("/auth/login-form", data=data)
    refresh_token = str(response_auth.json()["refresh_token"])

    refresh_data = json.dumps({"refresh_token": refresh_token})
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    response_tokens: Response = client_user.post(
        "/auth/refresh", headers=headers, content=refresh_data
    )

    assert response_tokens.status_code == 200
    assert response_tokens.json()["access_token"] != ""
    assert response_tokens.json()["refresh_token"] != ""
