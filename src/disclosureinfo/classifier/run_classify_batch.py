from __future__ import annotations

import sys
from typing import Any

import structlog
from sqlalchemy.orm import Session

from disclosureinfo.db import SessionLocal, get_settings
from disclosureinfo.services.classification_service import ClassificationService

logger = structlog.get_logger()


def run_batch(
    limit: int | None = None,
    has_detail: bool = False,
    update_existing: bool | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Run classification batch job.

    Args:
        limit: Maximum number of disclosures to classify (default from settings)
        has_detail: Only classify disclosures with detail (body_text)
        update_existing: Override update_existing setting
        verbose: Print detailed output

    Returns:
        Dict with stats and results
    """
    settings = get_settings()

    batch_limit = limit or settings.classify_batch_limit
    do_update = update_existing if update_existing is not None else settings.classify_update_existing

    if verbose:
        logger.info(
            "starting_classification_batch",
            limit=batch_limit,
            has_detail=has_detail,
            update_existing=do_update,
            version=settings.classifier_version,
        )

    db: Session = SessionLocal()
    try:
        service = ClassificationService(
            db=db,
            update_existing=do_update,
        )

        stats = service.classify_missing(
            limit=batch_limit,
            has_detail=has_detail,
        )

        result = {
            "processed": stats.processed,
            "created": stats.created,
            "skipped": stats.skipped,
            "updated": stats.updated,
            "failed": stats.failed,
            "errors": stats.errors,
        }

        if verbose:
            logger.info("classification_batch_complete", **result)
            print(f"\n=== Classification Batch Results ===")
            print(f"Processed: {stats.processed}")
            print(f"Created:   {stats.created}")
            print(f"Skipped:   {stats.skipped}")
            print(f"Updated:   {stats.updated}")
            print(f"Failed:    {stats.failed}")
            if stats.errors:
                print(f"\nErrors:")
                for err in stats.errors[:10]:
                    print(f"  - disclosure_id={err['disclosure_id']}: {err['error']}")
            print("=" * 40)

        return result

    finally:
        db.close()


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run rule-based classification on unclassified disclosures"
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=None,
        help="Number of disclosures to classify (default: from settings)"
    )
    parser.add_argument(
        "--has-detail", action="store_true",
        help="Only classify disclosures that have detail (body_text)"
    )
    parser.add_argument(
        "--update", action="store_true",
        help="Update existing classifications (default: skip)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print detailed output"
    )

    args = parser.parse_args()

    result = run_batch(
        limit=args.limit,
        has_detail=args.has_detail,
        update_existing=args.update if hasattr(args, 'update') else None,
        verbose=args.verbose,
    )

    # Exit code: 0 = success, 1 = failure
    if result["failed"] > 0 and result["processed"] == 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
