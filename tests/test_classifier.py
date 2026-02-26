from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from disclosureinfo.models import Base, Classification, Disclosure, DisclosureDetail
from disclosureinfo.classifier.rule_classifier import (
    RuleClassifier,
    CATEGORY_CORRECTION,
    CATEGORY_FINANCE,
    CATEGORY_OWNERSHIP,
    CATEGORY_CONTRACT,
    CATEGORY_MNA,
    CATEGORY_NEW_BIZ,
    CATEGORY_RELATED_PARTY,
    CATEGORY_OTHER,
)
from disclosureinfo.repositories import classification_repo
from disclosureinfo.services.classification_service import ClassificationService


def test_rule_classifier_correction_priority() -> None:
    """Test that correction keywords always return CORRECTION regardless of other matches."""
    classifier = RuleClassifier()

    # Test with Korean "정정" keyword
    result = classifier.classify(
        title="[정정] 2025 1분기 보고서",
        body="매출액 100억",
    )
    assert result.category == CATEGORY_CORRECTION
    assert result.confidence > 0

    # Test with Korean "취소" keyword
    result = classifier.classify(
        title="주식매매계약 취소 공시",
        body="합병 계약",
    )
    assert result.category == CATEGORY_CORRECTION

    # Test with Korean "번복" keyword
    result = classifier.classify(
        title="투자결정 번복 공시",
        body="재무제표",
    )
    assert result.category == CATEGORY_CORRECTION

    # Test with Korean "철회" keyword
    result = classifier.classify(
        title="기술양도 철회 안내",
        body="",
    )
    assert result.category == CATEGORY_CORRECTION

    # Test with correction keyword in body
    result = classifier.classify(
        title="2025 1분기 결산 공시",
        body="정정: 매출액 수정",
    )
    assert result.category == CATEGORY_CORRECTION


def test_rule_classifier_basic_categories() -> None:
    """Test basic category classification with representative fixtures."""
    classifier = RuleClassifier()

    # FINANCE: Financial keywords
    result = classifier.classify(
        title="2025 1분기 손익계산서",
        body="매출액 100억, 영업이익 20억",
    )
    assert result.category == CATEGORY_FINANCE

    result = classifier.classify(
        title="사업보고서 공시",
        body=None,
    )
    assert result.category == CATEGORY_FINANCE

    result = classifier.classify(
        title="분기보고서",
        body=None,
    )
    assert result.category == CATEGORY_FINANCE

    # OWNERSHIP: Ownership change keywords
    result = classifier.classify(
        title="주요주주 지분변동 공시",
        body="주식 보유 현황",
    )
    assert result.category == CATEGORY_OWNERSHIP

    result = classifier.classify(
        title="임원변경 공시",
        body="새로운 대표이사",
    )
    assert result.category == CATEGORY_OWNERSHIP

    result = classifier.classify(
        title="대표이사 변경",
        body=None,
    )
    assert result.category == CATEGORY_OWNERSHIP

    # CONTRACT: Contract keywords
    result = classifier.classify(
        title="시스템 구축 계약 체결",
        body="계약금액 500억",
    )
    assert result.category == CATEGORY_CONTRACT

    result = classifier.classify(
        title="수주공시",
        body="JV 계약",
    )
    assert result.category == CATEGORY_CONTRACT

    result = classifier.classify(
        title="공급계약",
        body=None,
    )
    assert result.category == CATEGORY_CONTRACT

    # MNA: Merger/Acquisition keywords
    result = classifier.classify(
        title="회사합병 공시",
        body="합병 한다",
    )
    assert result.category == CATEGORY_MNA

    result = classifier.classify(
        title="인수 공시",
        body="취득",
    )
    assert result.category == CATEGORY_MNA

    result = classifier.classify(
        title="자본투자 공시",
        body="VC 투자",
    )
    assert result.category == CATEGORY_MNA

    # NEW_BIZ: New business keywords
    result = classifier.classify(
        title="신규사업 진출 공시",
        body="신규 사업",
    )
    assert result.category == CATEGORY_NEW_BIZ

    result = classifier.classify(
        title="사업다각화",
        body="",
    )
    assert result.category == CATEGORY_NEW_BIZ

    # RELATED_PARTY: Related party transaction keywords
    result = classifier.classify(
        title="특수관계인 거래 공시",
        body="계열사 거래",
    )
    assert result.category == CATEGORY_RELATED_PARTY

    result = classifier.classify(
        title="자율공시",
        body="내부거래",
    )
    assert result.category == CATEGORY_RELATED_PARTY

    # OTHER: no matching pattern
    result = classifier.classify(
        title="일반 공시",
        body="내용 없음",
    )
    assert result.category == CATEGORY_OTHER


def test_classification_store_policy() -> None:
    """Test classification store policy (skip/update) with sqlite in-memory DB."""
    # Create in-memory SQLite DB
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        # Create disclosure with detail
        disclosure = Disclosure(
            guid="guid-1",
            link="http://example.com/1",
            title="2025 1분기 손익계산서",
            company_name="Test Corp",
        )
        db.add(disclosure)
        db.commit()
        db.refresh(disclosure)

        # Create detail
        detail = DisclosureDetail(
            disclosure_id=disclosure.id,
            body_text="매출액 100억",
        )
        db.add(detail)
        db.commit()

        # Test 1: First classification - should create
        service = ClassificationService(db=db, update_existing=False)
        action1, category1 = service.classify_and_store(disclosure.id)
        assert action1 == "created"
        assert category1 == CATEGORY_FINANCE

        # Verify classification exists
        classifications = classification_repo.list_by_disclosure_id(db, disclosure.id)
        assert len(classifications) == 1
        assert classifications[0].category == CATEGORY_FINANCE

        # Test 2: Second classification with same disclosure (update_existing=False) - should skip
        action2, category2 = service.classify_and_store(disclosure.id)
        assert action2 == "skipped"
        assert category2 == CATEGORY_FINANCE

        # Verify still only one classification
        classifications = classification_repo.list_by_disclosure_id(db, disclosure.id)
        assert len(classifications) == 1
        assert classifications[0].category == CATEGORY_FINANCE

        # Test 3: Third classification with update_existing=True - should update
        service_update = ClassificationService(db=db, update_existing=True)
        action3, category3 = service_update.classify_and_store(disclosure.id)
        assert action3 == "updated"

        # Verify still only one classification (updated)
        classifications = classification_repo.list_by_disclosure_id(db, disclosure.id)
        assert len(classifications) == 1
        assert classifications[0].category == CATEGORY_FINANCE

        # Test 4: Batch classification - classify_missing
        # Create another disclosure without classification
        disclosure2 = Disclosure(
            guid="guid-2",
            link="http://example.com/2",
            title="주요주주 지분변동",
        )
        db.add(disclosure2)
        db.commit()

        service_batch = ClassificationService(db=db, update_existing=False)
        stats = service_batch.classify_missing(limit=10)
        assert stats.processed == 1  # disclosure2 was just added and classified
        assert stats.created == 1  # It should be classified as OWNERSHIP
        assert stats.skipped == 0
        stats = service_batch.classify_missing(limit=10)
        assert stats.processed == 0  # No more unclassified disclosures
        assert stats.created == 0
        assert stats.skipped == 0
