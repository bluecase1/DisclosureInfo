from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import httpx

from disclosureinfo.fetcher.http_fetcher import HttpFetcher


def test_fetcher_timeout_retry() -> None:
    url = "http://example.com/detail"
    response = httpx.Response(
        status_code=200,
        headers={"content-type": "text/html; charset=utf-8"},
        content="<html><body>ok</body></html>".encode("utf-8"),
        request=httpx.Request("GET", url),
    )

    client = Mock()
    client.get.side_effect = [httpx.ReadTimeout("timeout"), response]

    settings = SimpleNamespace(
        detail_fetch_user_agent="DisclosureInfoTest/0.1",
        detail_fetch_accept_language="ko-KR,ko;q=0.9",
        detail_fetch_timeout_seconds=5,
        detail_fetch_max_bytes=2_000_000,
        detail_fetch_retry_attempts=3,
        detail_fetch_retry_min_seconds=0.01,
        detail_fetch_retry_max_seconds=0.05,
        request_delay_ms=0,
    )

    fetcher = HttpFetcher(settings=settings, client=client, sleep_fn=lambda _: None)
    result = fetcher.fetch_html(url)

    assert result is not None
    status_code, html_text = result
    assert status_code == 200
    assert "ok" in html_text
    assert client.get.call_count == 2
