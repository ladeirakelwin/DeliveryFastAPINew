from src.utils.senha import criptografar_senha, validar_senha

INVALID_VALUES = ["", None]


def test_senha_se_nao_consigo_criptografar_valores_de_senha_invalidos():
    for value in INVALID_VALUES:
        senha_invalida = criptografar_senha(value)

        assert senha_invalida == ""


def test_senha_se_nao_consigo_enviar_valores_invalidos_para_comparar_senhas():
    for value in INVALID_VALUES:
        senha_invalida = validar_senha(value, criptografar_senha(value))

        assert senha_invalida is False
