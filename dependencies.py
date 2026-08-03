from fastapi.security import OAuth2PasswordBearer
from settings import get_settings, Settings


settings = {}
initial_settings: Settings = get_settings()
settings = initial_settings.model_dump(mode="python")

DATABASE_URL = settings["DATABASE_URL"]
SECRET_KEY = settings["SECRET_KEY"]
ALGORITHM = settings["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = settings["ACCESS_TOKEN_EXPIRE_MINUTES"]
REFRESH_TOKEN_EXPIRE_DAYS = settings["REFRESH_TOKEN_EXPIRE_DAYS"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")
