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


def create_test_data(session_maker):
    """Create test disclosures with detail and classification."""
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


def test_list_disclosures_returns_data():
    """Test that list_disclosures returns data from DB."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    disclosures = create_test_data(session_maker)
    
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
        response = client.get("/api/v1/disclosures")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["items"]) == 3
        
        # Check structure
        item = data["items"][0]
        assert "id" in item
        assert "title" in item
        assert "company_name" in item
        assert "has_detail" in item
        
        # Items sorted by published_at DESC: d3 (Jan 17), d2 (Jan 16), d1 (Jan 15)
        assert data["items"][0]["has_detail"] == False
        assert data["items"][1]["has_detail"] == False
        assert data["items"][2]["has_detail"] == True
        
        print("PASSED: test_list_disclosures_returns_data")
    finally:
        app.dependency_overrides.clear()


def test_filter_by_category():
    """Test filtering by category."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data(session_maker)
    
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
        
        response = client.get("/api/v1/disclosures?category=FINANCE")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "FINANCE"
        
        response = client.get("/api/v1/disclosures?category=OWNERSHIP")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "OWNERSHIP"
        
        print("PASSED: test_filter_by_category")
    finally:
        app.dependency_overrides.clear()


def test_filter_by_company():
    """Test filtering by company name."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data(session_maker)
    
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
        assert data["total"] == 2
        
        print("PASSED: test_filter_by_company")
    finally:
        app.dependency_overrides.clear()


def test_limit_parameter():
    """Test limit parameter."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data(session_maker)
    
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
        
        response = client.get("/api/v1/disclosures?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["limit"] == 1
        
        print("PASSED: test_limit_parameter")
    finally:
        app.dependency_overrides.clear()


def test_get_disclosure_detail():
    """Test getting disclosure detail."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    disclosures = create_test_data(session_maker)
    
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


def test_get_disclosure_not_found():
    """Test 404 for non-existent disclosure."""
    engine = setup_test_db()
    session_maker = get_test_session_maker(engine)
    create_test_data(session_maker)
    
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
    import io
    
    print("=" * 60)
    print(f"API Tests Run at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    test_list_disclosures_returns_data()
    test_filter_by_category()
    test_filter_by_company()
    test_limit_parameter()
    test_get_disclosure_detail()
    test_get_disclosure_not_found()
    test_categories_endpoint()
    
    print("=" * 60)
    print("All 7 tests PASSED!")
    print("=" * 60)
