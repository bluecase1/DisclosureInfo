from fastapi import APIRouter, Query
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.get("/disclosures")
def list_disclosures(
    since: Optional[datetime] = Query(default=None),
    category: Optional[str] = Query(default=None),
    company: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    # TODO: connect DB and return results
    return {
        "items": [],
        "filters": {"since": since, "category": category, "company": company, "limit": limit},
    }

@router.get("/disclosures/{disclosure_id}")
def get_disclosure(disclosure_id: str):
    # TODO: connect DB and return detail
    return {"id": disclosure_id, "detail": None}

@router.get("/categories")
def categories():
    return {
        "categories": [
            "FINANCE", "OWNERSHIP", "CONTRACT", "MNA", "NEW_BIZ", "RELATED_PARTY", "CORRECTION", "OTHER"
        ]
    }
