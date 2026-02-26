# coding: utf-8
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from disclosureinfo.models import Disclosure, DisclosureDetail, Classification, ExtractedField


def list_disclosures(
    db: Session,
    since: datetime | None = None,
    category: str | None = None,
    company: str | None = None,
    limit: int = 50,
) -> tuple[list[Disclosure], int]:
    """
    List disclosures with optional filters.
    
    Returns:
        tuple of (disclosures, total_count)
    """
    # Base query
    query = select(Disclosure)
    count_query = select(func.count(Disclosure.id))
    
    # Apply filters
    if since:
        query = query.where(Disclosure.published_at >= since)
        count_query = count_query.where(Disclosure.published_at >= since)
    
    if company:
        query = query.where(Disclosure.company_name.ilike(f"%{company}%"))
        count_query = count_query.where(Disclosure.company_name.ilike(f"%{company}%"))
    
    # If category filter, join with classifications
    if category:
        query = query.join(Classification).where(Classification.category == category)
        count_query = count_query.join(Classification).where(Classification.category == category)
    
    # Get total count (before limit)
    total = db.execute(count_query).scalar() or 0
    
    # Order by published_at desc, then by id desc
    query = query.order_by(Disclosure.published_at.desc().nullslast(), Disclosure.id.desc())
    query = query.limit(limit)
    
    # Execute with eager loading for detail and classifications
    query = query.options(
        joinedload(Disclosure.detail),
        joinedload(Disclosure.classifications),
    )
    
    disclosures = list(db.execute(query).scalars().unique().all())
    query = query.options(joinedload(Disclosure.detail))
    
    disclosures = list(db.execute(query).scalars().unique().all())
    
    return disclosures, total


def get_disclosure_by_id(
    db: Session,
    disclosure_id: int,
) -> Disclosure | None:
    """
    Get disclosure by ID with all related data.
    
    Loads: detail, classifications, extracted_fields
    """
    query = (
        select(Disclosure)
        .where(Disclosure.id == disclosure_id)
        .options(
            joinedload(Disclosure.detail),
            joinedload(Disclosure.classifications),
            joinedload(Disclosure.extracted_fields),
        )
    )
    return db.execute(query).scalars().unique().one_or_none()


def get_latest_classification(
    db: Session,
    disclosure_id: int,
) -> Classification | None:
    """Get the latest classification for a disclosure."""
    query = (
        select(Classification)
        .where(Classification.disclosure_id == disclosure_id)
        .order_by(Classification.created_at.desc())
        .limit(1)
    )
    return db.execute(query).scalar_one_or_none()


def check_has_detail(db: Session, disclosure_id: int) -> bool:
    """Check if a disclosure has detail."""
    query = (
        select(DisclosureDetail)
        .where(DisclosureDetail.disclosure_id == disclosure_id)
    )
    return db.execute(query).scalar_one_or_none() is not None
