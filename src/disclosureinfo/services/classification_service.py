from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from disclosureinfo.classifier.rule_classifier import RuleClassifier
from disclosureinfo.repositories import classification_repo
from disclosureinfo.repositories.disclosure_detail_repo import get_detail_by_disclosure_id


@dataclass
class ClassificationStats:
    """Statistics from a batch classification run."""
    processed: int
    created: int
    skipped: int
    updated: int
    failed: int
    errors: list[dict[str, Any]]

    def __str__(self) -> str:
        return (
            f"ClassificationStats("
            f"processed={self.processed}, "
            f"created={self.created}, "
            f"skipped={self.skipped}, "
            f"updated={self.updated}, "
            f"failed={self.failed})"
        )


class ClassificationService:
    """Service for classifying disclosures using rule-based classifier."""

    def __init__(
        self,
        db: Session,
        classifier: RuleClassifier | None = None,
        update_existing: bool = False,
    ):
        self.db = db
        self.classifier = classifier or RuleClassifier()
        self.update_existing = update_existing

    def classify_and_store(
        self,
        disclosure_id: int,
    ) -> tuple[str, str]:
        """
        Classify a disclosure and store the result.

        Args:
            disclosure_id: The ID of the disclosure to classify

        Returns:
            tuple of (action, category) where action is "created" | "skipped" | "updated" | "failed"
        """
        try:
            # Get disclosure
            from disclosureinfo.repositories.disclosure_detail_repo import (
                get_disclosure_by_id,
            )

            disclosure = get_disclosure_by_id(self.db, disclosure_id)
            if not disclosure:
                return "failed", "N/A"

            # Get detail body text if available
            body_text: str | None = None
            if disclosure.detail and disclosure.detail.body_text:
                body_text = disclosure.detail.body_text

            # Classify
            result = self.classifier.classify(
                title=disclosure.title,
                body=body_text,
            )

            # Store
            _, action = classification_repo.save(
                db=self.db,
                disclosure_id=disclosure_id,
                category=result.category,
                confidence=result.confidence,
                evidence=result.evidence,
                version=result.version,
                update_existing=self.update_existing,
            )

            return action, result.category

        except Exception as e:
            # Log error but don't raise - allow batch to continue
            return "failed", str(e)

    def classify_missing(
        self,
        limit: int,
        has_detail: bool = False,
    ) -> ClassificationStats:
        """
        Classify disclosures that don't have classification yet.

        Args:
            limit: Maximum number to classify
            has_detail: If True, only classify disclosures with detail (body_text)

        Returns:
            ClassificationStats with run statistics
        """
        # Get disclosures without classification
        disclosures = classification_repo.list_disclosures_without_classification(
            db=self.db,
            limit=limit,
            has_detail=has_detail,
        )

        stats = ClassificationStats(
            processed=0,
            created=0,
            skipped=0,
            updated=0,
            failed=0,
            errors=[],
        )

        for disclosure in disclosures:
            stats.processed += 1
            action, category = self.classify_and_store(disclosure.id)

            if action == "created":
                stats.created += 1
            elif action == "skipped":
                stats.skipped += 1
            elif action == "updated":
                stats.updated += 1
            else:
                stats.failed += 1
                stats.errors.append({
                    "disclosure_id": disclosure.id,
                    "error": category,  # category contains error message
                })

        return stats
