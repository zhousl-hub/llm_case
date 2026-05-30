"""主应用程序入口"""
from fastapi import FastAPI
from routers import api_router
from config import settings
from middleware import setup_middleware

app = FastAPI(title="CloudEngine API", version="2.0.0")
setup_middleware(app)
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

@app.on_event("startup")
async def startup():
    from database import init_db
    await init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
