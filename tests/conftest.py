# coding: utf-8
from __future__ import annotations

import sys
import os
from pathlib import Path
from unittest.mock import patch

# Set test environment variables BEFORE importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("RSS_URL", "https://example.com/rss")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("DETAIL_FETCH_TIMEOUT_SECONDS", "15")
os.environ.setdefault("DETAIL_FETCH_MAX_BYTES", "2000000")
os.environ.setdefault("DETAIL_BODY_MAX_CHARS", "200000")
os.environ.setdefault("DETAIL_SAVE_RAW_HTML", "false")
os.environ.setdefault("DETAIL_UPDATE_EXISTING", "false")
os.environ.setdefault("REQUEST_DELAY_MS", "200")
os.environ.setdefault("DETAIL_FETCH_RETRY_ATTEMPTS", "3")
os.environ.setdefault("DETAIL_FETCH_RETRY_MIN_SECONDS", "0.5")
os.environ.setdefault("DETAIL_FETCH_RETRY_MAX_SECONDS", "5.0")
os.environ.setdefault("DETAIL_BATCH_SIZE", "50")
os.environ.setdefault("CLASSIFIER_VERSION", "rule-v1")
os.environ.setdefault("CLASSIFY_BATCH_LIMIT", "100")
os.environ.setdefault("CLASSIFY_UPDATE_EXISTING", "false")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
