FROM python:3.12.13-slim-bookworm

WORKDIR /code

# Copia os executáveis do uv de forma limpa
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Otimização de Cache: Copia apenas os arquivos de dependências primeiro
COPY pyproject.toml uv.lock /code/

# Instala as dependências (o uv cria o .venv automaticamente se não existir)
RUN uv sync --frozen --no-cache

# Copia o restante do código do seu projeto
COPY . /code

ENTRYPOINT ["./entrypoint.sh"]

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
