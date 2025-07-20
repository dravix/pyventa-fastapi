from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.dependencies import db

router = APIRouter()


@router.get("/")
def read_stores():
    stores = db.table("stores").select("*").execute()
    return {"stores": stores.data}


@router.get("/{store_id}")
def read_store(store_id: int):
    store = db.table("stores").select("*").eq("id", store_id).single().execute()
    return {"store_id": store_id, "store": store}
