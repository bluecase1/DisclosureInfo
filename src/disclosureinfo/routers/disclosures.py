# coding: utf-8
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from disclosureinfo.db import get_db
from disclosureinfo.repositories import disclosure_query_repo
from disclosureinfo.schemas import (
    DisclosureListItem,
    DisclosureListResponse,
    DisclosureDetailFullResponse,
    CategoryListResponse,
    ClassificationResponse,
    ExtractedFieldResponse,
    DisclosureDetailResponse,
)

router = APIRouter()


@router.get("/disclosures", response_model=DisclosureListResponse)
def list_disclosures(
    since: Optional[str] = Query(default=None, description="ISO datetime filter"),
    category: Optional[str] = Query(default=None, description="Category filter"),
    company: Optional[str] = Query(default=None, description="Company name filter"),
    limit: int = Query(default=50, ge=1, le=200, description="Max items to return"),
    cursor: Optional[str] = Query(default=None, description="Pagination cursor (format: published_at|id)"),
    db: Session = Depends(get_db),
):
    """List disclosures with cursor-based pagination and optional filters."""
    # Parse since datetime if provided
    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid since datetime format")
    
    # Query disclosures with cursor pagination
    disclosures, total, next_cursor = disclosure_query_repo.list_disclosures(
        db=db,
        since=since_dt,
        category=category,
        company=company,
        limit=limit,
        cursor=cursor,
    )
    
    # Build response items with category info
    items = []
    for d in disclosures:
        # Get latest classification category if available
        cat = None
        if d.classifications:
            # classifications is already loaded via joinedload
            latest = d.classifications[0] if d.classifications else None
            cat = latest.category if latest else None
        
        items.append(DisclosureListItem(
            id=d.id,
            title=d.title,
            company_name=d.company_name,
            published_at=d.published_at,
            link=d.link,
            has_detail=d.detail is not None,
            category=cat,
        ))
    
    return DisclosureListResponse(
        items=items,
        count=len(items),
        total=total,
        limit=limit,
        next_cursor=next_cursor,
        filters={"since": since, "category": category, "company": company},
    )


@router.get("/disclosures/{disclosure_id}", response_model=DisclosureDetailFullResponse)
def get_disclosure(
    disclosure_id: int,
    include_body: bool = Query(default=True, description="Include body_text in response"),
    body_max_chars: Optional[int] = Query(default=None, description="Truncate body_text to max chars"),
    db: Session = Depends(get_db),
):
    """Get disclosure detail by ID."""
    disclosure = disclosure_query_repo.get_disclosure_by_id(db, disclosure_id)
    
    if not disclosure:
        raise HTTPException(status_code=404, detail="Disclosure not found")
    
    # Build classification response (latest 1 only)
    classification = None
    if disclosure.classifications:
        latest = disclosure.classifications[0]  # Already sorted by created_at desc
        classification = ClassificationResponse.model_validate(latest)
    
    # Build extracted fields
    extracted_fields = []
    if disclosure.extracted_fields:
        for ef in disclosure.extracted_fields:
            extracted_fields.append(ExtractedFieldResponse.model_validate(ef))
    
    # Build detail response with body control
    detail = None
    if disclosure.detail:
        body_text = None
        if include_body and disclosure.detail.body_text:
            body_text = disclosure.detail.body_text
            if body_max_chars and len(body_text) > body_max_chars:
                body_text = body_text[:body_max_chars] + "..."
        
        detail = DisclosureDetailResponse(
            id=disclosure.detail.id,
            disclosure_id=disclosure.detail.disclosure_id,
            body_text=body_text,
            fetched_at=disclosure.detail.fetched_at,
        )
    
    return DisclosureDetailFullResponse(
        id=disclosure.id,
        title=disclosure.title,
        company_name=disclosure.company_name,
        published_at=disclosure.published_at,
        link=disclosure.link,
        guid=disclosure.guid,
        detail=detail,
        classification=classification,
        extracted_fields=extracted_fields,
        created_at=disclosure.created_at,
    )


@router.get("/categories", response_model=CategoryListResponse)
def categories():
    """Get supported categories."""
    return CategoryListResponse()
