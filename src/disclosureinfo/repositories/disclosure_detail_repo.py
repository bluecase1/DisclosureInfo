from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from disclosureinfo.models import Disclosure, DisclosureDetail


def get_disclosure_by_id(db: Session, disclosure_id: int) -> Disclosure | None:
    stmt = select(Disclosure).where(Disclosure.id == disclosure_id)
    return db.execute(stmt).scalar_one_or_none()


def get_disclosure_by_link(db: Session, link: str) -> Disclosure | None:
    stmt = select(Disclosure).where(Disclosure.link == link)
    return db.execute(stmt).scalar_one_or_none()


def list_disclosures_without_detail(db: Session, limit: int) -> list[Disclosure]:
    stmt = (
        select(Disclosure)
        .outerjoin(DisclosureDetail, DisclosureDetail.disclosure_id == Disclosure.id)
        .where(DisclosureDetail.id.is_(None))
        .order_by(Disclosure.published_at.desc().nullslast(), Disclosure.id.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def get_detail_by_disclosure_id(db: Session, disclosure_id: int) -> DisclosureDetail | None:
    stmt = select(DisclosureDetail).where(DisclosureDetail.disclosure_id == disclosure_id)
    return db.execute(stmt).scalar_one_or_none()


def save_detail(
    db: Session,
    disclosure_id: int,
    body_text: str,
    raw_html: str | None,
    update_existing: bool,
) -> tuple[DisclosureDetail, str]:
    existing = get_detail_by_disclosure_id(db, disclosure_id)
    if existing and not update_existing:
        return existing, "skipped"

    if existing:
        existing.body_text = body_text
        existing.raw_html = raw_html
        existing.fetched_at = datetime.now(timezone.utc)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing, "updated"

    detail = DisclosureDetail(
        disclosure_id=disclosure_id,
        body_text=body_text,
        raw_html=raw_html,
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail, "created"
