from __future__ import annotations

import logging
import time
from collections.abc import Callable

import httpx
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from disclosureinfo.settings import Settings


logger = logging.getLogger(__name__)


class HttpFetcher:
    def __init__(
        self,
        settings: Settings,
        client: httpx.Client | None = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.settings = settings
        self._client = client
        self._sleep_fn = sleep_fn

    def _headers(self) -> dict[str, str]:
        return {
            "User-Agent": self.settings.detail_fetch_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": self.settings.detail_fetch_accept_language,
            "Connection": "keep-alive",
        }

    def _fetch_once(self, url: str) -> tuple[int, str] | None:
        delay_seconds = max(0, self.settings.request_delay_ms) / 1000.0
        if delay_seconds > 0:
            self._sleep_fn(delay_seconds)

        client = self._client or httpx.Client(timeout=self.settings.detail_fetch_timeout_seconds)
        close_client = self._client is None

        try:
            response = client.get(url, headers=self._headers(), follow_redirects=True)
        finally:
            if close_client:
                client.close()

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "").lower()
            if "html" not in content_type:
                logger.warning("Non-HTML content skipped", extra={"url": url, "content_type": content_type})
                return None

            content = response.content[: self.settings.detail_fetch_max_bytes]
            encoding = response.encoding or "utf-8"
            html_text = content.decode(encoding, errors="replace")
            return response.status_code, html_text

        if response.status_code == 429 or 500 <= response.status_code < 600:
            request = response.request or httpx.Request("GET", url)
            raise httpx.HTTPStatusError(
                f"Retryable status code: {response.status_code}",
                request=request,
                response=response,
            )

        logger.warning("Non-success status skipped", extra={"url": url, "status_code": response.status_code})
        return None

    def fetch_html(self, url: str) -> tuple[int, str] | None:
        retryer = Retrying(
            stop=stop_after_attempt(max(1, self.settings.detail_fetch_retry_attempts)),
            wait=wait_random_exponential(
                multiplier=max(0.1, self.settings.detail_fetch_retry_min_seconds),
                max=max(self.settings.detail_fetch_retry_min_seconds, self.settings.detail_fetch_retry_max_seconds),
            ),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError)),
            reraise=True,
        )

        for attempt in retryer:
            with attempt:
                return self._fetch_once(url)

        return None


def fetch_html(url: str, settings: Settings) -> tuple[int, str] | None:
    fetcher = HttpFetcher(settings=settings)
    return fetcher.fetch_html(url)
