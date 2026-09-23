import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

package_dir = Path(__file__).resolve().parent
load_dotenv(package_dir / ".env")
load_dotenv(Path.cwd() / ".env")

try:
    from .Routers import UploadFile, CustomerSupport
except ImportError:
    from Routers import UploadFile, CustomerSupport


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://ragchatbog.netlify.app",
    )
    origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    # Allow any Netlify-hosted frontend in addition to explicit config values.
    netlify_origin = "https://ragchatbog.netlify.app"
    if netlify_origin not in origins:
        origins.append(netlify_origin)

    return origins


app = FastAPI(
    title="Customer Support API",
    version="1.0.0",
    description="Production-ready backend for the WhatsApp customer support and sales intelligence platform.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "service": "Customer Support API",
        "version": app.version,
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health", tags=["meta"])
def health_check() -> dict:
    return {"status": "ok", "service": "Customer Support API"}


app.include_router(UploadFile.router)
app.include_router(CustomerSupport.router)
# app.include_router(faq.router)
# app.include_router(chat.router)
