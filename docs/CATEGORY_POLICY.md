# Disclosure Categorization Policy

## Purpose
공시를 의미 있는 카테고리로 분류하고, 카테고리별로 외부 시스템에서 필요로 하는 핵심 필드를 표준화한다.

## Primary Categories (v0)
1. FINANCE (재무공시)
2. OWNERSHIP (지분/경영권 변동)
3. CONTRACT (계약/수주)
4. MNA (투자/합병/분할)
5. NEW_BIZ (신규사업)
6. RELATED_PARTY (내부거래)
7. CORRECTION (정정공시)
8. OTHER (기타)

## Classification Approach
- Stage A: Rule-based keyword/regex tagging (fast, deterministic)
- Stage B: AI Classification Agent (contextual)
- Stage C: Heuristic override (e.g., 정정/취소 패턴 우선)

### Output
- category: enum
- confidence: 0.0 ~ 1.0
- evidence: 규칙/키워드/근거 문장(가능한 범위)

## Required Fields Per Category (v0: 최소 세트)

### FINANCE
- company_name
- disclosed_at
- period (e.g., 2025Q4)
- revenue (optional)
- operating_profit (optional)
- net_income (optional)

### OWNERSHIP
- company_name
- disclosed_at
- actor (주요주주/임원 등)
- ownership_before (optional)
- ownership_after (optional)
- reason (optional)

### CONTRACT
- company_name
- disclosed_at
- counterparty (optional)
- contract_amount (optional)
- ratio_to_revenue (optional)
- start_date/end_date (optional)

### CORRECTION
- company_name
- disclosed_at
- original_disclosure_ref (optional)
- correction_reason (optional)

## Notes
- 필드 추출은 초기에는 heuristic + AI extraction 병행
- 모든 추출 결과는 provenance(출처/근거 텍스트)와 함께 저장
