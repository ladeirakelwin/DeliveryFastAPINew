from datetime import timedelta, datetime, timezone
from dependencies import (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS)
from fastapi.exceptions import HTTPException
from fastapi import status
import jwt

class AuthService:
    TOKEN_ERROR = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Erro ao gerar token! Tente novamente mais tarde.")
    expiracao_token = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expiracao_token =  datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
    def criar_token(self, data: dict, is_refresh_token: bool = False) -> str:
        try:
            token_cru = data.copy()
            token_cru.update({"exp": self.expiracao_token if not is_refresh_token else self.refresh_expiracao_token, "type": "access" if not is_refresh_token else "refresh"})
            token = jwt.encode(token_cru, SECRET_KEY, ALGORITHM)

        except Exception:
            raise self.TOKEN_ERROR
        
        return token
    
    @staticmethod
    def decodificar_token(token: str):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    def atualizar_token(self, refresh_token_codificado: str) -> tuple[str, str]:
        refresh_token = self.decodificar_token(refresh_token_codificado)

        if refresh_token.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não autorizado!")
        
        novo_refresh_token = self.criar_token({"sub": refresh_token.get("sub")}, True)
        novo_access_token = self.criar_token({"sub": refresh_token.get("sub")}, False)
        
        return novo_access_token, novo_refresh_token