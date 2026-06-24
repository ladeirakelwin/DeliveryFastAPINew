import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL")
    