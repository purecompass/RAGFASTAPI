from fastapi import FastAPI
from Routers import UploadFile

app = FastAPI(title="Multi-Tenant FAQ Service")

app.include_router(UploadFile.router)
# app.include_router(faq.router)
# app.include_router(chat.router)
