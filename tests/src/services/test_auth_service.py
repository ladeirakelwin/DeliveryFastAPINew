from src.services.auth_service import AuthService
from fastapi.exceptions import HTTPException
from time import sleep
import pytest


def test_auth_service_se_tokens_criados_em_tempos_distintos_tem_expiracoes_diferentes():
    auth_service: AuthService = AuthService()

    token_1 = auth_service.criar_token({"sub": "teste2"})
    sleep(1)
    token_2 = auth_service.criar_token({"sub": "teste3"})

    tempo_exp_1 = AuthService.decodificar_token(token_1)
    tempo_exp_2 = AuthService.decodificar_token(token_2)

    assert tempo_exp_1.get("exp") != tempo_exp_2.get("exp")


def test_auth_service_se_data_nao_conter_sub_ao_criar_token_retorna_vazio():
    auth_service = AuthService()

    token = auth_service.criar_token({})

    assert not token


def test_auth_service_se_gera_excecao_ao_enviar_dados_invalidos_ao_criar_token():
    auth_service = AuthService()

    with pytest.raises(HTTPException):
        auth_service.criar_token("sdasd")  # pyright: ignore[reportArgumentType]

    with pytest.raises(HTTPException):
        auth_service.criar_token({"sub": "asdasd"}, 11)  # pyright: ignore[reportArgumentType]

    with pytest.raises(HTTPException):
        auth_service.criar_token({"sub": "asdasd"}, True, "")  # pyright: ignore[reportArgumentType]


def test_auth_service_se_retorna_dict_vazio_quando_tentar_decodificar_token_vencido():
    # faça um mock de criar conta que retorne um token vencido e uma validação para inteiro positivo
    auth_service = AuthService()
    token_vencido = auth_service.criar_token({"sub": "sapopemba"}, False, -300)
    resposta_esperada = {}

    assert resposta_esperada == AuthService.decodificar_token(token_vencido)


def test_auth_service_se_enviar_valor_invalido_para_atualizar_token_ele_sobe_401():
    auth_service = AuthService()
    access_token = auth_service.criar_token({"sub": "sapopemba"})

    with pytest.raises(HTTPException):
        auth_service.atualizar_token("")

    with pytest.raises(HTTPException):
        auth_service.atualizar_token("sadojka12312123skldpóainsjdoaosdasdoasd")

    with pytest.raises(HTTPException):
        auth_service.atualizar_token(access_token)


def test_auth_service_se_ao_atualizar_token_valido_retorna_novos_token():
    auth_service = AuthService()

    refresh_token = auth_service.criar_token({"sub": "sapopemba"}, True)

    novo_access_token, novo_refresh_token = auth_service.atualizar_token(refresh_token)

    assert novo_access_token
    assert novo_refresh_token

    novo_access_token_decodificado = AuthService.decodificar_token(novo_access_token)
    novo_refresh_token_decodificado = AuthService.decodificar_token(novo_refresh_token)

    assert novo_access_token_decodificado.get("type") == "access"
    assert novo_refresh_token_decodificado.get("type") == "refresh"
