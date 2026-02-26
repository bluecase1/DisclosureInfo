# coding: utf-8
from __future__ import annotations

import sys
import os

# Set test environment variables BEFORE importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("RSS_URL", "https://example.com/rss")
os.environ.setdefault("LOG_LEVEL", "INFO")

# Import after setting env vars
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from disclosureinfo.models import Base, Disclosure, DisclosureDetail, Classification


# Test settings
TEST_DATABASE_URL = "sqlite:///:memory:"


def get_test_engine():
    """Create test engine with StaticPool for in-memory SQLite."""
    return create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def setup_test_db():
    """Create tables in test DB."""
    engine = get_test_engine()
    Base.metadata.create_all(bind=engine)
    return engine


def get_test_session_maker(engine):
    """Create session maker for test engine."""
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def create_test_data_pagination(session_maker):
    """Create test data for pagination testing (multiple items with different dates)."""
    with session_maker() as db:
        # Create 10 disclosures with different dates
        for i in range(10):
            d = Disclosure(
                guid=f"guid-{i+1}",
                link=f"http://example.com/{i+1}",
                title=f"공시 {i+1}",
                company_name="테스트회사",
                published_at=datetime(2025, 1, 10 + i, 10, 0, 0, tzinfo=timezone.utc),
            )
            db.add(d)
            db.flush()
            
            # Add classification to some
            if i % 2 == 0:
                class1 = Classification(
                    disclosure_id=d.id,
                    category="FINANCE" if i % 4 == 0 else "OWNERSHIP",
                    confidence=0.85,
                    evidence={"matches": []},
                    version="rule-v1",
                )
                db.add(class1)
            
            # Add detail to first 5
            if i < 5:
                detail = DisclosureDetail(
                    disclosure_id=d.id,
                    body_text=f"본문 내용 {i+1} - " + "a" * 100,  # Make body_text longer
                    raw_html="<html></html>",
                )
                db.add(detail)
        
        db.commit()


def create_basic_test_data(session_maker):
    """Create basic test data."""
    with session_maker() as db:
        # Disclosure 1: FINANCE (with detail)
        d1 = Disclosure(
            guid="guid-1",
            link="http://example.com/1",
            title="2025 1분기 손익계산서",
            company_name="테스트회사",
            published_at=datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        )
        db.add(d1)
        db.flush()
        
        detail1 = DisclosureDetail(
            disclosure_id=d1.id,
            body_text="매출액 100억원, 영업이익 20억원",
            raw_html="<html></html>",
        )
        db.add(detail1)
        
        class1 = Classification(
            disclosure_id=d1.id,
            category="FINANCE",
            confidence=0.85,
            evidence={"matches": []},
            version="rule-v1",
        )
        db.add(class1)
        
        # Disclosure 2: OWNERSHIP (without detail)
        d2 = Disclosure(
            guid="guid-2",
            link="http://example.com/2",
            title="주요주주 지분변동",
            company_name="테스트회사",
            published_at=datetime(2025, 1, 16, 10, 0, 0, tzinfo=timezone.utc),
        )
        db.add(d2)
        db.flush()
        
        class2 = Classification(
            disclosure_id=d2.id,
            category="OWNERSHIP",
            confidence=0.90,
            evidence={"matches": []},
            version="rule-v1",
        )
        db.add(class2)
        
        # Disclosure 3: No classification (without detail)
        d3 = Disclosure(
            guid="guid-3",
            link="http://example.com/3",
            title="일반 공시",
            company_name="다른회사",
            published_at=datetime(2025, 1, 17, 10, 0, 0, tzinfo=timezone.utc),
        )
        db.add(d3)
        
        db.commit()
        return [d1, d2, d3]


def test_list_returns_paginated_results():
    """Test that list_disclosures returns paginated results with count and total."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data_pagination(session_maker)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        # Test default limit (50)
        response = client.get("/api/v1/disclosures")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "count" in data
        assert "total" in data
        assert "limit" in data
        assert "next_cursor" in data
        
        # We created 10 items, limit default 50, so count should be 10, total 10
        assert data["count"] == 10
        assert data["total"] == 10
        assert data["limit"] == 50
        assert data["next_cursor"] is None  # No next page
        
        # Test custom limit
        response = client.get("/api/v1/disclosures?limit=3")
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 3
        assert data["total"] == 10
        assert data["limit"] == 3
        
        print("PASSED: test_list_returns_paginated_results")
    finally:
        app.dependency_overrides.clear()


def test_cursor_pagination():
    """Test cursor-based pagination."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data_pagination(session_maker)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        # First page
        response = client.get("/api/v1/disclosures?limit=3")
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 3
        assert data["next_cursor"] is not None
        
        first_page_items = data["items"]
        cursor = data["next_cursor"]
        
        # Second page using cursor
        response = client.get(f"/api/v1/disclosures?limit=3&cursor={cursor}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 3
        
        # Verify no overlap
        first_ids = [item["id"] for item in first_page_items]
        second_ids = [item["id"] for item in data["items"]]
        
        # No overlapping IDs
        assert len(set(first_ids) & set(second_ids)) == 0
        
        # Third page
        cursor2 = data["next_cursor"]
        response = client.get(f"/api/v1/disclosures?limit=3&cursor={cursor2}")
        data = response.json()
        
        assert data["count"] == 3
        
        # Fourth page (last one)
        cursor3 = data["next_cursor"]
        response = client.get(f"/api/v1/disclosures?limit=3&cursor={cursor3}")
        data = response.json()
        
        # Should have 1 item (total 10, 3+3+3+1 = 10)
        assert data["count"] == 1
        assert data["next_cursor"] is None  # Last page
        
        print("PASSED: test_cursor_pagination")
    finally:
        app.dependency_overrides.clear()


def test_filter_by_category():
    """Test filtering by category."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data_pagination(session_maker)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        # Filter by FINANCE (items 0, 4, 8 = 3 items)
        response = client.get("/api/v1/disclosures?category=FINANCE")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["items"][0]["category"] == "FINANCE"
        
        # Filter by OWNERSHIP (items 2, 6 = 2 items)
        response = client.get("/api/v1/disclosures?category=OWNERSHIP")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        
        print("PASSED: test_filter_by_category")
    finally:
        app.dependency_overrides.clear()


def test_filter_by_company():
    """Test filtering by company name."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data_pagination(session_maker)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        response = client.get("/api/v1/disclosures?company=테스트회사")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10  # All items have 테스트회사
        
        print("PASSED: test_filter_by_company")
    finally:
        app.dependency_overrides.clear()


def test_limit_parameter():
    """Test limit parameter."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data_pagination(session_maker)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        response = client.get("/api/v1/disclosures?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["limit"] == 5
        
        print("PASSED: test_limit_parameter")
    finally:
        app.dependency_overrides.clear()


def test_get_disclosure_detail():
    """Test getting disclosure detail."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    disclosures = create_basic_test_data(session_maker)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        # Get first disclosure (has detail + classification)
        response = client.get(f"/api/v1/disclosures/{disclosures[0].id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == disclosures[0].id
        assert data["title"] == "2025 1분기 손익계산서"
        assert data["detail"] is not None
        assert data["detail"]["body_text"] == "매출액 100억원, 영업이익 20억원"
        assert data["classification"] is not None
        assert data["classification"]["category"] == "FINANCE"
        assert "raw_html" not in data["detail"]
        
        print("PASSED: test_get_disclosure_detail")
    finally:
        app.dependency_overrides.clear()


def test_detail_include_body_option():
    """Test include_body=false option."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    disclosures = create_basic_test_data(session_maker)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        # Test include_body=false
        response = client.get(f"/api/v1/disclosures/{disclosures[0].id}?include_body=false")
        assert response.status_code == 200
        data = response.json()
        
        assert data["detail"] is not None
        assert data["detail"]["body_text"] is None  # Not included
        
        # Test body_max_chars
        response = client.get(f"/api/v1/disclosures/{disclosures[0].id}?body_max_chars=10")
        assert response.status_code == 200
        data = response.json()
        
        assert data["detail"]["body_text"] is not None
        assert len(data["detail"]["body_text"]) <= 13  # "매출액 100억..." = 13 chars with "..."
        
        print("PASSED: test_detail_include_body_option")
    finally:
        app.dependency_overrides.clear()


def test_get_disclosure_not_found():
    """Test 404 for non-existent disclosure."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_basic_test_data(session_maker)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        response = client.get("/api/v1/disclosures/99999")
        assert response.status_code == 404
        
        print("PASSED: test_get_disclosure_not_found")
    finally:
        app.dependency_overrides.clear()


def test_categories_endpoint():
    """Test categories endpoint returns enum values."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    
    from disclosureinfo.db import get_db
    from disclosureinfo.main import app
    
    def override_get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        assert "FINANCE" in data["categories"]
        assert "OWNERSHIP" in data["categories"]
        assert "CONTRACT" in data["categories"]
        assert "MNA" in data["categories"]
        assert "NEW_BIZ" in data["categories"]
        assert "RELATED_PARTY" in data["categories"]
        assert "CORRECTION" in data["categories"]
        assert "OTHER" in data["categories"]
        
        print("PASSED: test_categories_endpoint")
    finally:
        app.dependency_overrides.clear()


if __name__ == "__main__":
    from datetime import datetime
    
    print("=" * 60)
    print(f"API Tests Run at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    test_list_returns_paginated_results()
    test_cursor_pagination()
    test_filter_by_category()
    test_filter_by_company()
    test_limit_parameter()
    test_get_disclosure_detail()
    test_detail_include_body_option()
    test_get_disclosure_not_found()
    test_categories_endpoint()
    
    print("=" * 60)
    print("All 9 tests PASSED!")
    print("=" * 60)
