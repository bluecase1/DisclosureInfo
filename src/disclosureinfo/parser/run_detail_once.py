from __future__ import annotations

import argparse

from disclosureinfo.db import SessionLocal
from disclosureinfo.services.disclosure_detail_service import (
    process_disclosure_detail,
    process_disclosure_detail_by_url,
)
from disclosureinfo.settings import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and store a single disclosure detail")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--disclosure-id", type=int, help="target disclosure id")
    group.add_argument("--url", type=str, help="target disclosure detail URL")
    args = parser.parse_args()

    settings = Settings()
    with SessionLocal() as db:
        if args.disclosure_id is not None:
            result = process_disclosure_detail(db=db, disclosure_id=args.disclosure_id, settings=settings)
        else:
            result = process_disclosure_detail_by_url(db=db, link=args.url, settings=settings)

    print({"status": result.status, "disclosure_id": result.disclosure_id, "reason": result.reason})


if __name__ == "__main__":
    main()
