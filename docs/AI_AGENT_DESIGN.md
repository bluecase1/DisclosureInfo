# AI Agent Architecture

## Goal
공시 데이터의 분류/추출/요약/검증을 자동화하면서, 운영 안정성과 재현 가능성을 확보한다.

## Agents (v0)

### 1) Fetch Agent
- RSS 수집
- 신규/중복 판단
- 실패 재시도/레이트리밋

### 2) Parsing Agent
- 공시 상세 HTML → 텍스트 정제
- 핵심 메타데이터 추출

### 3) Classification Agent
- 카테고리 분류 + confidence
- 근거(evidence) 제공

### 4) Extraction Agent
- 카테고리별 required fields 추출
- 숫자/날짜 normalization

### 5) Summarization Agent
- 한 줄/3줄 요약
- 키포인트 bullet

### 6) Validation Agent
- 누락 필드 점검
- 이상치(상식 범위 밖) 플래그
- 룰 기반 검증 + LLM 검증(선택)

## Orchestration Model
- 기본: Pipeline (collector → parser → classify → extract → validate → store)
- 확장: Event-driven (queue 기반)로 단계별 worker scale-out

## Reliability Requirements
- Prompt/versioning: 프롬프트/모델/규칙 버전 저장
- Deterministic fallback: AI 실패 시 규칙 기반 결과라도 제공
- Observability: agent latency, error rate, confidence distribution 기록
