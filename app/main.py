from typing import Union
import os
from supabase import create_client, Client
from app.identity.routes import router as identity_router
from app.memberships.router import router as memberships_router
from app.stores.router import router as stores_router
from app.companies.router import router as companies_router

from fastapi import FastAPI

app = FastAPI()

app.include_router(identity_router, prefix="/identity", tags=["identity"])
app.include_router(memberships_router, prefix="/memberships", tags=["memberships"])
app.include_router(stores_router, prefix="/stores", tags=["stores"])
app.include_router(companies_router, prefix="/companies", tags=["companies"])


@app.get("/")
def read_root():
    return {"Status": "UP", "Version": "0.1.0", "Vibe": "😉"}
