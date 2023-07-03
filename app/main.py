from fastapi import FastAPI
from app.routers import lei_router

app = FastAPI()

app.include_router(lei_router.router, prefix="/api")
