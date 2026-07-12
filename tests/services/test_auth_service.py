from src.services.auth_service import AuthService
from time import sleep


def test_auth_service_se_tokens_criados_em_tempos_distintos_tem_expiracoes_diferentes():
    auth_service: AuthService = AuthService()

    token_1 = auth_service.criar_token({"sub": "teste2"})
    sleep(1)
    token_2 = auth_service.criar_token({"sub": "teste3"})

    tempo_exp_1 = AuthService.decodificar_token(token_1)
    tempo_exp_2 = AuthService.decodificar_token(token_2)

    assert tempo_exp_1.get("exp") != tempo_exp_2.get("exp")
