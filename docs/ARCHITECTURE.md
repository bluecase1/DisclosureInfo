# System Architecture

## Architecture Style
Modular Monolith (MVP) → Queue-based scale-out (v1)

## Components
1. API Layer (FastAPI)
2. Collector Worker (RSS + Detail fetch)
3. AI Processing Layer (agents; can run in worker)
4. Storage Layer (PostgreSQL)
5. Cache/Queue (Redis) [optional at MVP; recommended for v1]
6. Observability (logs/metrics/health)

## Data Model (High-Level)
- disclosures: raw item + normalized
- disclosure_details: body/attachments
- classifications: category/confidence/evidence/version
- extracted_fields: key/value + provenance + version

## Scalability
- API stateless
- Worker 수평 확장
- Queue 사용 시 단계별 병렬 처리
- DB index 최적화(시간/회사/카테고리)

## Deployment
- Docker 기반
- env 기반 설정 (12-factor)
- infra: docker-compose (dev) + k8s (optional later)

## Maintenance / Solution Packaging
- modules 분리: collector / parsing / ai / api / storage
- contracts: Pydantic schema + OpenAPI
- plugin-friendly: oh-my-opencode로 반복 패턴 자동화
