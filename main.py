from fastapi import FastAPI
from routes import router
from middleware import AuthMiddleware

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(router)