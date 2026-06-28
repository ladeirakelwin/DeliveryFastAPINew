from datetime import timedelta, datetime, timezone
from dependencies import SECRET_KEY, ALGORITHM
from fastapi.exceptions import HTTPException
from fastapi import status
import jwt

class AuthService:
    def __init__(self, expiracao_token: int = 30):
        self.expiracao_token = datetime.now(timezone.utc) + timedelta(minutes=expiracao_token)

    def criar_access_token(self, data: dict) -> str:
        try:
            token_cru = data.copy()
            token_cru.update({"exp": self.expiracao_token})
            token = jwt.encode(token_cru, SECRET_KEY, ALGORITHM)

        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Erro ao gerar access token! Tente novamente mais tarde.")
        return token
    
    @staticmethod
    def decodificar_token(token: str):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
