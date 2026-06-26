from pwdlib import PasswordHash

password_hash: PasswordHash = PasswordHash.recommended()

def criptografar_senha(senha: str | None) -> str:
    if not senha:
        return ""
    
    return password_hash.hash(senha)

def validar_senha(senha: str | None, senha_criptograda: str | None) -> bool:
    if not senha or not senha_criptograda:
        return False
    
    return password_hash.verify(senha, senha_criptograda)


