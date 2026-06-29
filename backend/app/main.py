from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, documents, shares, versions
from app.ws import router as ws_router

app = FastAPI(title="DocEditor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(shares.router, prefix="/api/documents", tags=["shares"])
app.include_router(versions.router, prefix="/api/documents", tags=["versions"])
app.include_router(ws_router.router, tags=["websocket"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
