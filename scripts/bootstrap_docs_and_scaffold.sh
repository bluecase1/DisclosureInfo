#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/bootstrap_docs_and_scaffold.sh
# Creates docs + basic FastAPI scaffold in the current repo.

mkdir -p docs src/disclosureinfo/routers scripts infra tests

echo "✅ Created folders."
echo "Now copy the md contents from docs/ and scaffold files as needed."
