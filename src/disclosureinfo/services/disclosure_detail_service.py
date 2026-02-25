from __future__ import annotations

from dataclasses import dataclass
import logging

from sqlalchemy.orm import Session

from disclosureinfo.fetcher.http_fetcher import HttpFetcher
from disclosureinfo.parser.detail_parser import parse_detail_html
from disclosureinfo.repositories.disclosure_detail_repo import (
    get_disclosure_by_id,
    get_disclosure_by_link,
    save_detail,
)
from disclosureinfo.settings import Settings


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DetailProcessResult:
    status: str
    disclosure_id: int | None
    reason: str | None = None


def process_disclosure_detail(db: Session, disclosure_id: int, settings: Settings) -> DetailProcessResult:
    disclosure = get_disclosure_by_id(db, disclosure_id)
    if disclosure is None:
        return DetailProcessResult(status="skipped", disclosure_id=None, reason="disclosure_not_found")

    if not disclosure.link:
        return DetailProcessResult(status="skipped", disclosure_id=disclosure.id, reason="missing_link")

    return _process_with_link(db=db, disclosure_id=disclosure.id, link=disclosure.link, settings=settings)


def process_disclosure_detail_by_url(db: Session, link: str, settings: Settings) -> DetailProcessResult:
    disclosure = get_disclosure_by_link(db, link)
    if disclosure is None:
        return DetailProcessResult(status="skipped", disclosure_id=None, reason="disclosure_not_found_by_url")

    return _process_with_link(db=db, disclosure_id=disclosure.id, link=link, settings=settings)


def _process_with_link(db: Session, disclosure_id: int, link: str, settings: Settings) -> DetailProcessResult:
    fetcher = HttpFetcher(settings=settings)

    try:
        fetch_result = fetcher.fetch_html(link)
    except Exception as exc:  # network errors must not stop pipeline
        logger.exception("detail fetch failed", extra={"disclosure_id": disclosure_id, "link": link})
        return DetailProcessResult(status="failed", disclosure_id=disclosure_id, reason=str(exc))

    if fetch_result is None:
        return DetailProcessResult(status="skipped", disclosure_id=disclosure_id, reason="fetch_skipped")

    _, html_text = fetch_result
    parsed = parse_detail_html(html_text=html_text, body_max_chars=settings.detail_body_max_chars)

    if not parsed.body_text:
        return DetailProcessResult(status="skipped", disclosure_id=disclosure_id, reason="empty_body_text")

    raw_html = parsed.raw_html if settings.detail_save_raw_html else None
    if raw_html is not None and len(raw_html.encode("utf-8")) > settings.detail_fetch_max_bytes:
        raw_html = raw_html[: settings.detail_fetch_max_bytes]

    _, action = save_detail(
        db=db,
        disclosure_id=disclosure_id,
        body_text=parsed.body_text,
        raw_html=raw_html,
        update_existing=settings.detail_update_existing,
    )
    return DetailProcessResult(status=action, disclosure_id=disclosure_id)
