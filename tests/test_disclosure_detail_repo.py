from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from disclosureinfo.models import Base, Disclosure
from disclosureinfo.repositories.disclosure_detail_repo import get_detail_by_disclosure_id, save_detail


def test_store_detail_1to1() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        disclosure = Disclosure(
            guid="guid-1",
            link="http://example.com/1",
            title="공시 1",
        )
        db.add(disclosure)
        db.commit()
        db.refresh(disclosure)

        _, action_1 = save_detail(
            db=db,
            disclosure_id=disclosure.id,
            body_text="본문 1",
            raw_html=None,
            update_existing=False,
        )
        assert action_1 == "created"

        detail_after_first = get_detail_by_disclosure_id(db=db, disclosure_id=disclosure.id)
        assert detail_after_first is not None
        assert detail_after_first.body_text == "본문 1"

        _, action_2 = save_detail(
            db=db,
            disclosure_id=disclosure.id,
            body_text="본문 2",
            raw_html="<html></html>",
            update_existing=False,
        )
        assert action_2 == "skipped"

        detail_after_second = get_detail_by_disclosure_id(db=db, disclosure_id=disclosure.id)
        assert detail_after_second is not None
        assert detail_after_second.body_text == "본문 1"
