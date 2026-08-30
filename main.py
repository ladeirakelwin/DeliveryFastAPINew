from fastapi import FastAPI, status
from src.routes import orders
from database import DBSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import time
from src.routes import auth
from fastapi.responses import JSONResponse
from loguru import logger
from src.utils.logging import setup_logging


setup_logging()

app = FastAPI()


@app.get("/health", tags=["Healthcheck"])
def healthcheck(db: DBSession):
    start_time = time.time()
    try:
        db.execute(text("Select 1"))
        latency = (time.time() - start_time) * 1000
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
        }
    except SQLAlchemyError:
        # Crucial: Rollback prevents the session from getting stuck in a broken transaction state
        db.rollback()

        # Extract the underlying database engine error message if available
        logger.exception("Erro no health check: ")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
            },
        )
    except Exception:
        logger.exception("Erro no healthcheck: ")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
            },
        )


app.include_router(auth.auth_routes)
app.include_router(orders.order_routes)
