# coding: utf-8
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClassificationResponse(BaseModel):
    """Classification response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    category: str
    confidence: float | None = None
    evidence: dict[str, Any] | None = None
    version: str | None = None
    created_at: datetime


class ExtractedFieldResponse(BaseModel):
    """Extracted field response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    category: str
    field_key: str
    field_value: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    version: str | None = None
    created_at: datetime


class DisclosureDetailResponse(BaseModel):
    """Disclosure detail response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    disclosure_id: int
    body_text: str | None = None
    fetched_at: datetime


class DisclosureListItem(BaseModel):
    """Disclosure list item schema (minimal info)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    company_name: str | None = None
    published_at: datetime | None = None
    link: str
    has_detail: bool = False
    category: str | None = None


class DisclosureDetailFullResponse(BaseModel):
    """Full disclosure detail response with all related data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    company_name: str | None = None
    published_at: datetime | None = None
    link: str
    guid: str | None = None
    detail: DisclosureDetailResponse | None = None
    classification: ClassificationResponse | None = None
    extracted_fields: list[ExtractedFieldResponse] = Field(default_factory=list)
    created_at: datetime


class CategoryListResponse(BaseModel):
    """Categories list response."""
    categories: list[str] = Field(
        default=[
            "FINANCE",
            "OWNERSHIP", 
            "CONTRACT",
            "MNA",
            "NEW_BIZ",
            "RELATED_PARTY",
            "CORRECTION",
            "OTHER",
        ]
    )


class DisclosureListResponse(BaseModel):
    """Disclosure list response with pagination info."""
    items: list[DisclosureListItem]
    total: int
    limit: int
    filters: dict[str, Any] = Field(default_factory=dict)
