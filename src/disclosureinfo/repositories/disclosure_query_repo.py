# coding: utf-8
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select, or_
from sqlalchemy.orm import Session, joinedload

from disclosureinfo.models import Disclosure, DisclosureDetail, Classification, ExtractedField


def list_disclosures(
    db: Session,
    since: datetime | None = None,
    category: str | None = None,
    company: str | None = None,
    limit: int = 50,
    cursor: str | None = None,
) -> tuple[list[Disclosure], int, str | None]:
    """
    List disclosures with cursor-based pagination and optional filters.
    
    Args:
        db: Database session
        since: Filter by published_at >= since
        category: Filter by classification category
        company: Filter by company name (partial match)
        limit: Max items per page
        cursor: Cursor for pagination (format: "published_at|id")
    
    Returns:
        tuple of (disclosures, total_count, next_cursor)
    """
    # Parse cursor if provided
    cursor_published_at = None
    cursor_id = None
    if cursor:
        try:
            cursor_parts = cursor.split("|")
            if len(cursor_parts) == 2:
                cursor_published_at = datetime.fromisoformat(cursor_parts[0].replace("Z", "+00:00"))
                cursor_id = int(cursor_parts[1])
        except (ValueError, AttributeError):
            pass  # Invalid cursor ignored
    
    # Base query
    query = select(Disclosure)
    
    # Apply filters
    if since:
        query = query.where(Disclosure.published_at >= since)
    
    if company:
        query = query.where(Disclosure.company_name.ilike(f"%{company}%"))
    
    if category:
        query = query.join(Classification).where(Classification.category == category)
    
    # Count total (before cursor filter)
    count_query = select(func.count(Disclosure.id))
    if since:
        count_query = count_query.where(Disclosure.published_at >= since)
    if company:
        count_query = count_query.where(Disclosure.company_name.ilike(f"%{company}%"))
    if category:
        count_query = count_query.join(Classification).where(Classification.category == category)
    total = db.execute(count_query).scalar() or 0
    
    # Apply cursor filter for pagination
    # Cursor logic: get items BEFORE the cursor position
    if cursor_published_at is not None and cursor_id is not None:
        # Get items published_at < cursor_published_at OR 
        # (published_at == cursor_published_at AND id < cursor_id)
        cursor_condition = or_(
            Disclosure.published_at < cursor_published_at,
            and_(
                Disclosure.published_at == cursor_published_at,
                Disclosure.id < cursor_id
            )
        )
        query = query.where(cursor_condition)
    
    # Order by published_at desc, id desc
    query = query.order_by(Disclosure.published_at.desc().nullslast(), Disclosure.id.desc())
    query = query.limit(limit + 1)  # Fetch one extra to check if there's a next page
    
    # Execute with eager loading
    query = query.options(
        joinedload(Disclosure.detail),
        joinedload(Disclosure.classifications),
    )
    
    disclosures = list(db.execute(query).scalars().unique().all())
    
    # Determine next_cursor
    next_cursor = None
    if len(disclosures) > limit:
        disclosures = disclosures[:limit]  # Remove extra item
        last = disclosures[-1]
        if last.published_at:
            next_cursor = f"{last.published_at.isoformat()}|{last.id}"
    
    return disclosures, total, next_cursor


def count_disclosures(
    db: Session,
    since: datetime | None = None,
    category: str | None = None,
    company: str | None = None,
) -> int:
    """Count disclosures matching filters."""
    query = select(func.count(Disclosure.id))
    
    if since:
        query = query.where(Disclosure.published_at >= since)
    
    if company:
        query = query.where(Disclosure.company_name.ilike(f"%{company}%"))
    
    if category:
        query = query.join(Classification).where(Classification.category == category)
    
    return db.execute(query).scalar() or 0


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
