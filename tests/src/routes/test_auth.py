from httpx2 import Response
from fastapi.exceptions import HTTPException
import pytest


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
