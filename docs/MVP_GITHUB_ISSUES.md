# MVP GitHub Issues (Draft)

아래 이슈는 현재 레포 상태(`docs/SYSTEM_RULES.md`, `docs/PROJECT.md` 기준)에서 바로 생성 가능한 GitHub Issues 포맷 초안이다.

## Issue 1
**Title**: `[P0] DB 기반 계층 구축 (engine/session/models/migrations)`

**Body**
```md
## 배경
MVP 데이터 저장/조회의 기반이 되는 DB 계층이 아직 없다.

## 작업 내용
- SQLAlchemy engine/session 구성
- ORM 모델 추가: disclosures, disclosure_details, classifications, extracted_fields
- Alembic 초기 마이그레이션 생성
- 중복제거용 unique key/인덱스 정의

## 완료 조건 (Acceptance Criteria)
- 앱 실행 시 DB 연결 성공
- 마이그레이션 up/down 정상 동작
- 핵심 테이블/인덱스가 스키마에 반영됨

## 의존성
- 없음

## Labels
- priority:P0
- area:storage
- type:feature
```

## Issue 2
**Title**: `[P0] RSS Collector Worker 및 폴링 스케줄 구현`

**Body**
```md
## 배경
PROJECT DoD의 "RSS 폴링 → 신규 항목 적재"를 만족하려면 수집 워커가 필요하다.

## 작업 내용
- RSS fetch loop/스케줄 구현
- poll interval env 설정 반영
- 신규 항목 raw/normalized 적재 파이프라인 연결

## 완료 조건 (Acceptance Criteria)
- 주기적으로 RSS를 읽고 신규 항목 저장
- 동일 데이터 재수집 시 중복 삽입 방지 경로와 연동 가능

## 의존성
- Issue 1

## Labels
- priority:P0
- area:collector
- type:feature
```

## Issue 3
**Title**: `[P0] 중복 제거 및 정규화 키(dedup key) 구현`

**Body**
```md
## 배경
SYSTEM_RULES/PROJECT 모두 중복 제거를 필수 요구사항으로 명시한다.

## 작업 내용
- guid/link/title/pubDate 기반 정규화 규칙 정의
- dedup key(hash) 생성 로직 구현
- DB unique constraint + upsert 정책 적용

## 완료 조건 (Acceptance Criteria)
- 동일 공시 재수집 시 신규 insert 0건
- 정규화 규칙 테스트 통과

## 의존성
- Issue 1
- Issue 2

## Labels
- priority:P0
- area:collector
- area:storage
- type:feature
```

## Issue 4
**Title**: `[P0] 공시 상세 페이지 파서 구현`

**Body**
```md
## 배경
MVP DoD에서 상세 본문 파싱(제목/본문/링크/일시/회사 식별)이 요구된다.

## 작업 내용
- 상세 페이지 fetch/parse 모듈 구현
- 제목/본문/회사/공시시각/첨부 메타 추출
- raw + normalized 저장 연결

## 완료 조건 (Acceptance Criteria)
- 상세 파싱 결과가 DB에 저장됨
- 최소 필드(제목/본문 텍스트/링크/일시/회사 식별) 충족

## 의존성
- Issue 1
- Issue 2

## Labels
- priority:P0
- area:parsing
- type:feature
```

## Issue 5
**Title**: `[P0] API DB 와이어링 및 API_SPEC 경로 정합`

**Body**
```md
## 배경
현재 disclosures API는 placeholder 응답이며 스펙 일부와 경로 불일치가 있다.

## 작업 내용
- `/api/v1/disclosures` DB 조회 연결
- `/api/v1/disclosures/{id}` 상세 조회 연결
- `/api/v1/categories` 정책 기반 응답 연결
- `/api/v1/companies/{company}/disclosures` 경로 추가
- health 경로 전략 문서/코드 정합화 (`/health` vs `/api/v1/health`)

## 완료 조건 (Acceptance Criteria)
- placeholder TODO 제거
- API_SPEC와 실제 라우트 정합
- 목록/상세/카테고리 조회가 DB 결과 반환

## 의존성
- Issue 1
- Issue 3
- Issue 4

## Labels
- priority:P0
- area:api
- type:feature
```

## Issue 6
**Title**: `[P0] 운영 최소셋: health/readiness, metrics, 구조화 로그`

**Body**
```md
## 배경
PROJECT DoD에 기본 모니터링(health, metrics/log)이 명시돼 있다.

## 작업 내용
- liveness/readiness health 분리
- metrics endpoint 추가
- structlog 기반 구조화 로깅 적용

## 완료 조건 (Acceptance Criteria)
- health/readiness/metrics 접근 가능
- 요청/에러 로그가 구조화 포맷으로 남음

## 의존성
- Issue 1
- Issue 5

## Labels
- priority:P0
- area:observability
- type:feature
```

## Issue 7
**Title**: `[P0] 테스트 기반선 구축 (unit + API 통합)`

**Body**
```md
## 배경
SYSTEM_RULES는 주요 모듈 테스트 가능성을 필수로 요구한다.

## 작업 내용
- pytest 설정/디렉토리 구성
- 중복제거/파싱/재시도 로직 단위 테스트
- disclosures API 통합 테스트

## 완료 조건 (Acceptance Criteria)
- 핵심 모듈 테스트 존재 및 통과
- 회귀 방지 가능한 최소 테스트 세트 확보

## 의존성
- Issue 3
- Issue 4
- Issue 5
- Issue 6

## Labels
- priority:P0
- area:test
- type:test
```

## Issue 8
**Title**: `[P1] 분류 엔진 v0 (Rule-first + AI fallback 인터페이스)`

**Body**
```md
## 배경
CATEGORY_POLICY 기반 카테고리 분류와 confidence/evidence 산출이 필요하다.

## 작업 내용
- 룰 기반 분류기 구현
- confidence/evidence 산출
- AI 분류 인터페이스 + deterministic fallback 계약 정의

## 완료 조건 (Acceptance Criteria)
- 분류 결과(category/confidence/evidence) 저장
- AI 실패 시 룰 기반 결과 반환

## 의존성
- Issue 1
- Issue 4

## Labels
- priority:P1
- area:classification
- type:feature
```

## Issue 9
**Title**: `[P1] 카테고리별 필드 추출 v0 (최소 1~2개 카테고리)`

**Body**
```md
## 배경
PROJECT DoD는 카테고리별 필수 필드 추출을 요구한다.

## 작업 내용
- FINANCE/CONTRACT 등 1~2개 카테고리 필드 추출 구현
- 추출 결과 provenance 저장

## 완료 조건 (Acceptance Criteria)
- 선택 카테고리에서 필수 필드 추출 성공
- provenance와 함께 DB 저장

## 의존성
- Issue 8

## Labels
- priority:P1
- area:extraction
- type:feature
```

## Issue 10
**Title**: `[P1] 정정공시 추적 및 버전 이력 연결`

**Body**
```md
## 배경
PROJECT는 정정 추적을 운영 요구사항으로 명시한다.

## 작업 내용
- 원공시 참조/제목 패턴/updated 시간 기반 정정 탐지
- 기존 공시와 정정 공시 연결 및 이력 저장

## 완료 조건 (Acceptance Criteria)
- 정정 케이스에서 원공시-정정공시 관계 조회 가능
- 이력 손실 없이 버전 데이터 보존

## 의존성
- Issue 3
- Issue 4

## Labels
- priority:P1
- area:tracking
- type:feature
```
