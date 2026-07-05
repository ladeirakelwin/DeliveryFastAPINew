from fastapi import FastAPI
from routes import auth, orders
from database import DBSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import time

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
            "error": None
        }
    except SQLAlchemyError as err:
        # Crucial: Rollback prevents the session from getting stuck in a broken transaction state
        db.rollback()
        
        # Extract the underlying database engine error message if available
        error_msg = str(err.__dict__.get('orig', err))
        return {
            "status": "unhealthy",
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "error": error_msg
        }
    except Exception as err:
        return {
            "status": "unhealthy",
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "error": str(err)
        }

app.include_router(auth.auth_routes)
app.include_router(orders.order_routes)