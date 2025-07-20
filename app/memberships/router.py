from fastapi import APIRouter, Depends
from app.dependencies import (
    db,
)  # Assuming you have a dependencies.py that provides the supabase client

router = APIRouter()


@router.get("/")
def read_memberships():
    memberships = db.table("membership_catalog").select("*").execute()
    return {"memberships": memberships.data}


@router.get("/{membership_id}")
def read_membership(membership_id: int):
    membership = (
        db.table("membership_catalog")
        .select("*")
        .eq("id", membership_id)
        .single()
        .execute()
    )
    return {"membership_id": membership_id, "membership": membership}
