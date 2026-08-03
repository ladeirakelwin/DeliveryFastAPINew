from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import PydanticCustomError, ValidationError
from functools import lru_cache
from pydantic import field_validator

class Settings(BaseSettings):
    app_name: str = "DELIVERYFASTAPINEW"
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3

    @field_validator("DATABASE_URL","SECRET_KEY", mode="before")
    @classmethod
    def validar_variaveis_ambiente_str(cls, value: str):

        if not value:
            raise PydanticCustomError(
                "EnvDependenciesError", "Está faltando as variáveis de ambiente: SECRET_KEY e/ou DATABASE_URL"
            )

        return value

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()