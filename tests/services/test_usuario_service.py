from src.services.usuario_service import UsuarioService
from models import Usuario

VALID_USERS: list = [
    {"nome": "adm", "senha": "adm"},
    {"nome": "teste", "senha": "teste"},
]
INVALID_USERS: list = [
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
