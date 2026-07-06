import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = str(os.getenv("ALGORITHM"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 3))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")
