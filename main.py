from fastapi import FastAPI
from routes import auth, orders

app = FastAPI()

app.include_router(auth.auth_routes)
app.include_router(orders.order_routes)