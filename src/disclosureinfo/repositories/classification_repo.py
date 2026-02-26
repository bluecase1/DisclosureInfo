from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from disclosureinfo.models import Classification, Disclosure


def get_by_disclosure_id(
    db: Session,
    disclosure_id: int,
    version: str | None = None,
) -> Classification | None:
    """Get classification for a disclosure. If version provided, get specific version."""
    stmt = select(Classification).where(
        Classification.disclosure_id == disclosure_id
    )
    if version:
        stmt = stmt.where(Classification.version == version)
    stmt = stmt.order_by(Classification.created_at.desc())
    return db.execute(stmt).scalar_one_or_none()


def get_latest_by_disclosure_id(
    db: Session,
    disclosure_id: int,
) -> Classification | None:
    """Get the latest classification for a disclosure (any version)."""
    stmt = (
        select(Classification)
        .where(Classification.disclosure_id == disclosure_id)
        .order_by(Classification.created_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_by_disclosure_id(
    db: Session,
    disclosure_id: int,
) -> list[Classification]:
    """List all classifications for a disclosure (ordered by created_at desc)."""
    stmt = (
        select(Classification)
        .where(Classification.disclosure_id == disclosure_id)
        .order_by(Classification.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def has_classification(
    db: Session,
    disclosure_id: int,
) -> bool:
    """Check if a disclosure already has a classification."""
    return get_latest_by_disclosure_id(db, disclosure_id) is not None


def save(
    db: Session,
    disclosure_id: int,
    category: str,
    confidence: float,
    evidence: dict[str, Any] | None,
    version: str,
    update_existing: bool = False,
) -> tuple[Classification, str]:
    """
    Save or update a classification.

    Policy:
    - If update_existing=False (default): skip if exists, return ("skipped")
    - If update_existing=True: update the latest classification or create new

    Returns:
        tuple of (Classification, action) where action is "created" | "updated" | "skipped"
    """
    existing = get_latest_by_disclosure_id(db, disclosure_id)

    if existing and not update_existing:
        return existing, "skipped"

    if existing and update_existing:
        # Update existing classification
        existing.category = category
        existing.confidence = confidence
        existing.evidence = evidence
        existing.version = version
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing, "updated"

    # Create new classification
    classification = Classification(
        disclosure_id=disclosure_id,
        category=category,
        confidence=confidence,
        evidence=evidence,
        version=version,
    )
    db.add(classification)
    db.commit()
    db.refresh(classification)
    return classification, "created"


def delete_all_for_disclosure(
    db: Session,
    disclosure_id: int,
) -> int:
    """Delete all classifications for a disclosure. Returns count deleted."""
    stmt = delete(Classification).where(
        Classification.disclosure_id == disclosure_id
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount


def list_disclosures_without_classification(
    db: Session,
    limit: int,
    has_detail: bool = False,
) -> list[Disclosure]:
    """
    List disclosures without classification.

    Args:
        db: Database session
        limit: Maximum number to return
        has_detail: If True, only return disclosures that have detail (body_text)
    """
    from disclosureinfo.models import DisclosureDetail

    # Subquery to find disclosures with classification
    classified_subq = (
        select(Classification.disclosure_id)
        .distinct()
    ).subquery()

    stmt = (
        select(Disclosure)
        .where(Disclosure.id.notin_(select(classified_subq)))
        .order_by(Disclosure.published_at.desc().nullslast(), Disclosure.id.desc())
        .limit(limit)
    )

    disclosures = list(db.execute(stmt).scalars().all())

    if has_detail:
        # Filter to only those with detail (contains body_text)
        filtered = []
        for d in disclosures:
            if d.detail and d.detail.body_text:
                filtered.append(d)
        return filtered[:limit]

    return disclosures
