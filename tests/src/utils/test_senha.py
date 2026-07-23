from src.utils.senha import criptografar_senha

INVALID_VALUES = ["", None]


def test_senha_se_nao_consigo_criptografar_valores_de_senha_invalidos():
    for value in INVALID_VALUES:
        senha_invalida = criptografar_senha(value)

        assert senha_invalida == ""
