from __future__ import annotations

from pathlib import Path

from disclosureinfo.parser.detail_parser import parse_detail_html


def test_detail_parser_extracts_body() -> None:
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "detail_sample.html"
    html = fixture_path.read_text(encoding="utf-8")

    parsed = parse_detail_html(html)

    assert parsed.title == "테스트 공시 제목"
    assert "공시 본문 텍스트 추출 테스트" in parsed.body_text
    assert "핵심 문장 A." in parsed.body_text
    assert "상단 메뉴" not in parsed.body_text
