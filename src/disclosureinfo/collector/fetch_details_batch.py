from __future__ import annotations

import argparse
import logging

from disclosureinfo.db import SessionLocal
from disclosureinfo.repositories.disclosure_detail_repo import list_disclosures_without_detail
from disclosureinfo.services.disclosure_detail_service import process_disclosure_detail
from disclosureinfo.settings import Settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run(limit: int | None = None) -> dict[str, int]:
    settings = Settings()
    batch_limit = limit if limit is not None else settings.detail_batch_size

    stats = {
        "processed": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0,
    }

    with SessionLocal() as db:
        disclosures = list_disclosures_without_detail(db=db, limit=batch_limit)

        for disclosure in disclosures:
            result = process_disclosure_detail(db=db, disclosure_id=disclosure.id, settings=settings)
            stats["processed"] += 1
            if result.status in stats:
                stats[result.status] += 1
            else:
                stats["failed"] += 1

            logger.info(
                "detail_batch_item",
                extra={
                    "disclosure_id": disclosure.id,
                    "status": result.status,
                    "reason": result.reason,
                },
            )

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and store disclosure detail pages in batch")
    parser.add_argument("--limit", type=int, default=None, help="maximum disclosures to process")
    args = parser.parse_args()

    stats = run(limit=args.limit)
    print(stats)


if __name__ == "__main__":
    main()
