FROM python:3.12.13-slim-bookworm

WORKDIR /code

COPY --from=ghcr.io/astral-sh/uv:0.11.27 /uv /uvx /bin/

COPY . /code

EXPOSE 8000

RUN uv sync && uv run alembic upgrade head

ENTRYPOINT ["uv", "run","uvicorn","main:app","--host", "0.0.0.0" , "--reload"]