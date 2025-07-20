from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.dependencies import db

router = APIRouter()


@router.get("/")
def read_companies():
    companies = db.table("companies").select("*").execute()
    return {"companies": companies.data}


@router.get("/{company_id}")
def read_company(company_id: int):
    try:
        company = (
            db.table("companies").select("*").eq("id", company_id).single().execute()
        )
        if not company.data:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"company_id": company_id, "company": company}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{company_id}/products")
def read_company_products(company_id: int):
    products = db.table("products").select("*").eq("company_id", company_id).execute()
    return {"company_id": company_id, "products": products.data}
