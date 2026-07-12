from datetime import timedelta, datetime, timezone
from dependencies import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from fastapi.exceptions import HTTPException
from fastapi import status
from jwt.exceptions import ExpiredSignatureError
import jwt


class AuthService:
    TOKEN_ERROR = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Erro ao gerar token! Tente novamente mais tarde.",
    )

    def criar_token(
        self,
        data: dict,
        is_refresh_token: bool = False,
        expiracao_token: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expiracao_token: int = REFRESH_TOKEN_EXPIRE_DAYS,
    ) -> str:

        if not isinstance(is_refresh_token, bool):
            raise self.TOKEN_ERROR

        if not data.get("sub"):
            return ""

        try:
            tempo_expiracao_token = datetime.now(timezone.utc) + timedelta(
                minutes=expiracao_token
            )
            tempo_refresh_expiracao_token = datetime.now(timezone.utc) + timedelta(
                days=refresh_expiracao_token
            )

            token_cru = data.copy()
            token_cru.update(
                {
                    "exp": tempo_expiracao_token
                    if not is_refresh_token
                    else tempo_refresh_expiracao_token,
                    "type": "access" if not is_refresh_token else "refresh",
                }
            )
            token = jwt.encode(token_cru, SECRET_KEY, ALGORITHM)

        except Exception:
            raise self.TOKEN_ERROR

        return token

    @staticmethod
    def decodificar_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except ExpiredSignatureError:
            return {}

    def atualizar_token(self, refresh_token_codificado: str) -> tuple[str, str]:
        refresh_token = self.decodificar_token(refresh_token_codificado)

        if not refresh_token or refresh_token.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autorizado ou token expirado!",
            )

        novo_refresh_token = self.criar_token({"sub": refresh_token.get("sub")}, True)
        novo_access_token = self.criar_token({"sub": refresh_token.get("sub")}, False)

        return novo_access_token, novo_refresh_token
