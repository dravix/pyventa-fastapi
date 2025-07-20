from pydantic import BaseModel
from typing import Optional


class MembershipCatalog(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    duration_days: int
    is_active: bool
