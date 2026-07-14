from src.services.usuario_service import UsuarioService
from fastapi.exceptions import HTTPException
import pytest

VALID_USERS: list = [
    {"nome": "adm", "email": "adm@adm.com", "senha": "adm"},
    {"nome": "teste", "email": "teste@test.com", "senha": "teste"},
]
INVALID_USERS: list = [
    {"nome": "nonecxiste", "senha": "nonecxiste"},
    {"nome": "inativoa", "senha": "inativoa"},
    {"nome": "inativoa", "senha": "inativoa"},
]


def test_usuario_service_se_consigo_autenticar_usuario_valido(user_seeded_db):
    usuario_service = UsuarioService(user_seeded_db)

    for usuario in VALID_USERS:
        usuario_autenticado = usuario_service.autenticar_usuario(
            usuario.get("nome"), usuario.get("senha")
        )
        assert usuario.get("nome") == usuario_autenticado.nome
        assert (
            hasattr(usuario_autenticado, "nome")
            and hasattr(usuario_autenticado, "email")
            and hasattr(usuario_autenticado, "senha")
            and hasattr(usuario_autenticado, "admin")
            and hasattr(usuario_autenticado, "ativo")
        )


def test_usuario_service_se_nao_consigo_logar_com_usuario_invalido_ou_inativo(
    user_seeded_db,
):
    usuario_service = UsuarioService(user_seeded_db)

    with pytest.raises(HTTPException) as scenario_1:
        usuario_service.autenticar_usuario(
            INVALID_USERS[0].get("nome"), INVALID_USERS[0].get("senha")
        )
        assert scenario_1.value.status_code == 401
        assert scenario_1.value.detail == "Usuário ou senha inválido!"

    with pytest.raises(HTTPException) as scenario_2:
        usuario_service.autenticar_usuario(
            INVALID_USERS[1].get("nome"), INVALID_USERS[1].get("senha")
        )

        assert scenario_2.value.status_code == 403
        assert scenario_2.value.detail == "Usuário inativo!"

    with pytest.raises(HTTPException) as scenario_3:
        usuario_service.autenticar_usuario(
            INVALID_USERS[2].get("nome"), INVALID_USERS[2].get("senha")
        )

        assert scenario_3.value.status_code == 403
        assert scenario_3.value.detail == "Usuário inativo!"


def test_usuario_service_se_criando_usuario_novo(mock_get_db):
    usuario_novo = VALID_USERS[0]

    usuario_service = UsuarioService(mock_get_db)

    usuario_criado = usuario_service.criar_usuario(
        usuario_novo.get("email"), usuario_novo.get("nome"), usuario_novo.get("senha")
    )

    assert usuario_novo.get("nome") == usuario_criado.nome
    assert (
        hasattr(usuario_criado, "nome")
        and hasattr(usuario_criado, "email")
        and hasattr(usuario_criado, "senha")
        and hasattr(usuario_criado, "admin")
        and hasattr(usuario_criado, "ativo")
    )


def test_usuario_service_se_nao_sera_possivel_criar_usuario_existente(user_seeded_db):
    usuario_service = UsuarioService(user_seeded_db)

    for usuario_test in VALID_USERS:
        with pytest.raises(HTTPException) as scenario:
            usuario_service.criar_usuario(
                usuario_test.get("email"),
                usuario_test.get("nome"),
                usuario_test.get("senha"),
            )

        assert scenario.value.status_code == 409
        assert scenario.value.detail == "Conta já existe!"
