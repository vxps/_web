from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.session import engine
from database.init_db import init_db
from routers import products

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()

app = FastAPI(
    title="LampShop Product Service",
    description="РњРёРєСЂРѕСЃРµСЂРІРёСЃ СѓРїСЂР°РІР»РµРЅРёСЏ С‚РѕРІР°СЂР°РјРё",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "product-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)