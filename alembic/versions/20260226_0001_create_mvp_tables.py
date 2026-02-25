"""create MVP disclosure tables

Revision ID: 20260226_0001
Revises:
Create Date: 2026-02-26 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260226_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "disclosures",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("guid", sa.String(length=512), nullable=True),
        sa.Column("link", sa.String(length=1024), nullable=False),
        sa.Column("title", sa.String(length=1000), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("raw_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("guid", name="uq_disclosures_guid"),
        sa.UniqueConstraint("link", name="uq_disclosures_link"),
    )
    op.create_index("ix_disclosures_published_at", "disclosures", ["published_at"])
    op.create_index("ix_disclosures_company_name", "disclosures", ["company_name"])

    op.create_table(
        "disclosure_details",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("disclosure_id", sa.BigInteger(), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("raw_html", sa.Text(), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["disclosure_id"], ["disclosures.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("disclosure_id", name="uq_disclosure_details_disclosure_id"),
    )

    op.create_table(
        "classifications",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("disclosure_id", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["disclosure_id"], ["disclosures.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_classifications_disclosure_id", "classifications", ["disclosure_id"])
    op.create_index("ix_classifications_category", "classifications", ["category"])

    op.create_table(
        "extracted_fields",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("disclosure_id", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("field_key", sa.String(length=128), nullable=False),
        sa.Column("field_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("provenance", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["disclosure_id"], ["disclosures.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_extracted_fields_disclosure_id", "extracted_fields", ["disclosure_id"])
    op.create_index("ix_extracted_fields_category", "extracted_fields", ["category"])


def downgrade() -> None:
    op.drop_index("ix_extracted_fields_category", table_name="extracted_fields")
    op.drop_index("ix_extracted_fields_disclosure_id", table_name="extracted_fields")
    op.drop_table("extracted_fields")

    op.drop_index("ix_classifications_category", table_name="classifications")
    op.drop_index("ix_classifications_disclosure_id", table_name="classifications")
    op.drop_table("classifications")

    op.drop_table("disclosure_details")

    op.drop_index("ix_disclosures_company_name", table_name="disclosures")
    op.drop_index("ix_disclosures_published_at", table_name="disclosures")
    op.drop_table("disclosures")
