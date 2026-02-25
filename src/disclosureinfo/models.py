from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


JsonValue = JSON().with_variant(JSONB(), "postgresql")


class Base(DeclarativeBase):
    pass


class Disclosure(Base):
    __tablename__ = "disclosures"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guid: Mapped[str | None] = mapped_column(String(512), unique=True, nullable=True)
    link: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    company_name: Mapped[str | None] = mapped_column(String(255), index=True)
    raw_json: Mapped[dict[str, Any] | None] = mapped_column(JsonValue)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    detail: Mapped[DisclosureDetail | None] = relationship(
        back_populates="disclosure",
        uselist=False,
        cascade="all, delete-orphan",
    )
    classifications: Mapped[list[Classification]] = relationship(
        back_populates="disclosure",
        cascade="all, delete-orphan",
    )
    extracted_fields: Mapped[list[ExtractedField]] = relationship(
        back_populates="disclosure",
        cascade="all, delete-orphan",
    )


class DisclosureDetail(Base):
    __tablename__ = "disclosure_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    disclosure_id: Mapped[int] = mapped_column(
        ForeignKey("disclosures.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    body_text: Mapped[str | None] = mapped_column(Text)
    raw_html: Mapped[str | None] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    disclosure: Mapped[Disclosure] = relationship(back_populates="detail")


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    disclosure_id: Mapped[int] = mapped_column(
        ForeignKey("disclosures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    confidence: Mapped[float | None] = mapped_column(Float)
    evidence: Mapped[dict[str, Any] | None] = mapped_column(JsonValue)
    version: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    disclosure: Mapped[Disclosure] = relationship(back_populates="classifications")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    disclosure_id: Mapped[int] = mapped_column(
        ForeignKey("disclosures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    field_key: Mapped[str] = mapped_column(String(128), nullable=False)
    field_value: Mapped[dict[str, Any] | None] = mapped_column(JsonValue)
    provenance: Mapped[dict[str, Any] | None] = mapped_column(JsonValue)
    version: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    disclosure: Mapped[Disclosure] = relationship(back_populates="extracted_fields")
