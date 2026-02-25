from __future__ import annotations

from dataclasses import dataclass
import re

from bs4 import BeautifulSoup


@dataclass(slots=True)
class ParsedDetail:
    title: str | None
    body_text: str
    raw_html: str | None


_REMOVE_TAGS = ("script", "style", "noscript", "nav", "header", "footer", "aside", "iframe")
_CANDIDATE_SELECTORS = (
    "#content",
    ".content",
    "#container",
    ".article",
    "article",
    "main",
    "#viewer",
)


def _normalize_whitespace(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text)
    return normalized.strip()


def parse_detail_html(html_text: str, body_max_chars: int = 200_000) -> ParsedDetail:
    soup = BeautifulSoup(html_text, "lxml")

    for tag in _REMOVE_TAGS:
        for node in soup.find_all(tag):
            node.decompose()

    title = None
    if soup.title and soup.title.string:
        title = _normalize_whitespace(soup.title.string)

    candidate_text = ""
    for selector in _CANDIDATE_SELECTORS:
        candidate = soup.select_one(selector)
        if candidate:
            text = _normalize_whitespace(candidate.get_text(" ", strip=True))
            if len(text) >= 20:
                candidate_text = text
                break

    if not candidate_text:
        candidate_text = _normalize_whitespace(soup.get_text(" ", strip=True))

    if body_max_chars > 0 and len(candidate_text) > body_max_chars:
        candidate_text = candidate_text[:body_max_chars]

    return ParsedDetail(
        title=title,
        body_text=candidate_text,
        raw_html=html_text,
    )
