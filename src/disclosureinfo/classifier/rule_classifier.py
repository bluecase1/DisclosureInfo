# coding: utf-8
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Sequence

CATEGORY_FINANCE = "FINANCE"
CATEGORY_OWNERSHIP = "OWNERSHIP"
CATEGORY_CONTRACT = "CONTRACT"
CATEGORY_MNA = "MNA"
CATEGORY_NEW_BIZ = "NEW_BIZ"
CATEGORY_RELATED_PARTY = "RELATED_PARTY"
CATEGORY_CORRECTION = "CORRECTION"
CATEGORY_OTHER = "OTHER"

VALID_CATEGORIES = frozenset([
    CATEGORY_FINANCE,
    CATEGORY_OWNERSHIP,
    CATEGORY_CONTRACT,
    CATEGORY_MNA,
    CATEGORY_NEW_BIZ,
    CATEGORY_RELATED_PARTY,
    CATEGORY_CORRECTION,
    CATEGORY_OTHER,
])

@dataclass
class ClassificationResult:
    category: str
    confidence: float
    evidence: dict[str, Any]
    version: str

TITLE_MATCH_WEIGHT = 2.0
BODY_MATCH_WEIGHT = 1.0
MIN_CONFIDENCE_THRESHOLD = 0.1

class RuleClassifier:
    def __init__(self, version: str = "rule-v1"):
        self.version = version
        self._rules = self._build_rules()

    def _build_rules(self):
        return {
            CATEGORY_CORRECTION: [
                ("정정", re.IGNORECASE, 1.0),
                ("취소", re.IGNORECASE, 1.0),
                ("번복", re.IGNORECASE, 1.0),
                ("철회", re.IGNORECASE, 1.0),
                ("수정", re.IGNORECASE, 0.8),
                ("삭제", re.IGNORECASE, 0.8),
            ],
            CATEGORY_FINANCE: [
                ("손익계산서|재무제표|결산|분기보고서|사업보고서", re.IGNORECASE, 1.5),
                ("매출액|영업이익|순이익|당기순이익|총이익|흑자|적자", re.IGNORECASE, 1.2),
                ("재무현황|재무성과|경영실적|실적", re.IGNORECASE, 1.0),
                ("주식발행|증자|감자|유상증자|무상증자", re.IGNORECASE, 1.0),
                ("매출액[0-9,]+|영업이익[0-9,]+|순이익[0-9,]+", re.IGNORECASE, 0.8),
                ("재무제표.*검증|회계감사", re.IGNORECASE, 0.8),
            ],
            CATEGORY_OWNERSHIP: [
                ("주요주주|대주주|특수관계인|지분变动|지분변동", re.IGNORECASE, 1.5),
                ("임원变动|임원변경|대표이사|사외이사", re.IGNORECASE, 1.3),
                ("경영권|지분매수|지분양도|매수|RTO", re.IGNORECASE, 1.2),
                ("주식교환|회사합병|분할|分割", re.IGNORECASE, 1.0),
                ("소유주식|보유주식|변동비율", re.IGNORECASE, 0.8),
            ],
            CATEGORY_CONTRACT: [
                ("계약|수주|조달|발주", re.IGNORECASE, 1.5),
                ("공급계약|구매계약|판매계약", re.IGNORECASE, 1.3),
                ("금액[0-9,]+|계약금액|수주금액", re.IGNORECASE, 1.2),
                (" JV |컨소시엄|공동수급", re.IGNORECASE, 1.0),
                ("계약기간|계약서|계약.*체결", re.IGNORECASE, 0.8),
            ],
            CATEGORY_MNA: [
                ("합병|병합|인수|매수", re.IGNORECASE, 1.5),
                ("투자|출자|자본투자|VC", re.IGNORECASE, 1.3),
                ("分割|분할|분리|신규설립", re.IGNORECASE, 1.2),
                ("자회사|계열사|종속회사", re.IGNORECASE, 1.0),
                ("목적회사|취득|purchase", re.IGNORECASE, 0.8),
            ],
            CATEGORY_NEW_BIZ: [
                ("신규사업|신사업|새로운사업", re.IGNORECASE, 1.5),
                ("사업영역.*확장|사업다각화", re.IGNORECASE, 1.3),
                ("진출|입찰|수산업무", re.IGNORECASE, 1.2),
                ("사업타당성|타당성.*조사", re.IGNORECASE, 1.0),
                ("新能源|신에너지|친환경", re.IGNORECASE, 0.8),
            ],
            CATEGORY_RELATED_PARTY: [
                ("특수관계인|내부거래|관계사", re.IGNORECASE, 1.5),
                ("자율공시|자율적.*공시", re.IGNORECASE, 1.3),
                ("계열사.*거래|모회사|종속회사", re.IGNORECASE, 1.2),
                ("임원.*거래|이사회.*승인", re.IGNORECASE, 1.0),
                ("동일인이|발행인과", re.IGNORECASE, 0.8),
            ],
        }

    def _match_text(self, text: str, weight: float, categories: Sequence[str] | None = None) -> tuple[float, list[dict[str, Any]]]:
        """Match patterns in text and return score + evidence.
        
        Args:
            text: Text to search
            weight: Weight multiplier (TITLE_MATCH_WEIGHT or BODY_MATCH_WEIGHT)
            categories: Optional list of categories to match. If None, matches all categories.
        """
        if not text:
            return 0.0, []
        
        total_score = 0.0
        evidence: list[dict[str, Any]] = []
        
        # Filter to specific categories if provided
        if categories is not None:
            rules_to_check = {k: v for k, v in self._rules.items() if k in categories}
        else:
            rules_to_check = self._rules
        
        for category, rules in rules_to_check.items():
            for pattern_str, flags, base_score in rules:
                pattern = re.compile(pattern_str, flags)
                matches = pattern.findall(text)
                if matches:
                    match_count = len(matches)
                    category_score = base_score * min(match_count, 3) * weight
                    total_score += category_score
                    evidence.append({
                        "category": category,
                        "matched": pattern_str,
                        "matches": matches[:5],
                        "weight": weight,
                        "base_score": base_score,
                    })
        
        return total_score, evidence

    def classify(self, title: str, body: str | None) -> ClassificationResult:
        """Classify a disclosure based on title and body text."""
        # Priority 1: Check CORRECTION patterns only (mandatory override)
        correction_score, correction_evidence = self._match_text(
            title, TITLE_MATCH_WEIGHT, categories=[CATEGORY_CORRECTION]
        )
        if body:
            body_correction_score, body_correction_evidence = self._match_text(
                body, BODY_MATCH_WEIGHT, categories=[CATEGORY_CORRECTION]
            )
            correction_score += body_correction_score
            correction_evidence.extend(body_correction_evidence)

        if correction_score >= 1.0:
            return ClassificationResult(
                category=CATEGORY_CORRECTION,
                confidence=min(correction_score / 10.0, 1.0),
                evidence={"matches": correction_evidence, "priority": "CORRECTION"},
                version=self.version,
            )

        # Priority 2: Check all other categories (excluding CORRECTION)
        category_scores: dict[str, float] = {}
        category_evidence: dict[str, list[dict[str, Any]]] = {}

        # Title matches (higher weight)
        title_score, title_evidence = self._match_text(title, TITLE_MATCH_WEIGHT)
        for ev in title_evidence:
            cat = ev["category"]
            if cat != CATEGORY_CORRECTION:
                category_scores[cat] = category_scores.get(cat, 0.0) + ev["base_score"] * TITLE_MATCH_WEIGHT
                category_evidence.setdefault(cat, []).append(ev)

        # Body matches (lower weight)
        if body:
            body_score, body_evidence = self._match_text(body, BODY_MATCH_WEIGHT)
            for ev in body_evidence:
                cat = ev["category"]
                if cat != CATEGORY_CORRECTION:
                    category_scores[cat] = category_scores.get(cat, 0.0) + ev["base_score"] * BODY_MATCH_WEIGHT
                    category_evidence.setdefault(cat, []).append(ev)

        if not category_scores:
            return ClassificationResult(
                category=CATEGORY_OTHER,
                confidence=0.0,
                evidence={"reason": "no_matching_pattern"},
                version=self.version,
            )

        best_category = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        best_evidence = category_evidence.get(best_category, [])

        confidence = min(best_score / 5.0, 1.0)

        if confidence < MIN_CONFIDENCE_THRESHOLD:
            return ClassificationResult(
                category=CATEGORY_OTHER,
                confidence=0.0,
                evidence={"reason": "below_threshold", "scores": category_scores},
                version=self.version,
            )

        return ClassificationResult(
            category=best_category,
            confidence=confidence,
            evidence={"matches": best_evidence, "scores": category_scores},
            version=self.version,
        )

default_classifier = RuleClassifier()

def classify(title: str, body: str | None = None) -> ClassificationResult:
    return default_classifier.classify(title, body)
