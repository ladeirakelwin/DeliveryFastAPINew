from datetime import timedelta, datetime, timezone
from dependencies import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from jwt.exceptions import ExpiredSignatureError, DecodeError
from src.utils.exceptions import TOKEN_ERROR, UNAUTHORIZED_USER
from loguru import logger
import jwt


class AuthService:
    def criar_token(
        self,
        data: dict,
        is_refresh_token: bool = False,
        expiracao_token: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expiracao_token: int = REFRESH_TOKEN_EXPIRE_DAYS,
    ) -> str:

        if not isinstance(is_refresh_token, bool):
            logger.error("Erro ao criar token se a flag de is_rf não é booleana")
            raise TOKEN_ERROR

        try:
            if not data.get("sub"):
                return ""

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
            logger.exception("Erro ao criar token: ")
            raise TOKEN_ERROR

        return token

    @staticmethod
    def decodificar_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except (ExpiredSignatureError, DecodeError, Exception):
            logger.exception("Erro ao decodificar token: ")
            return {}

    def atualizar_token(self, refresh_token_codificado: str) -> tuple[str, str]:
        refresh_token = self.decodificar_token(refresh_token_codificado)

        if not refresh_token or refresh_token.get("type") != "refresh":
            logger.error("Error ao atualizar token: ")
            raise UNAUTHORIZED_USER

        novo_refresh_token = self.criar_token({"sub": refresh_token.get("sub")}, True)
        novo_access_token = self.criar_token({"sub": refresh_token.get("sub")}, False)

        return novo_access_token, novo_refresh_token
