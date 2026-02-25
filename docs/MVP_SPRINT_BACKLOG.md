# MVP Sprint Backlog (Executable Order)

아래 백로그는 이슈 의존성을 기준으로 "바로 실행 가능한 구현 순서"로 분해했다.

## Sprint 0 (기반 구축, 1주)
- 목표: 데이터 계층/수집 파이프라인의 최소 실행선 확보
- 포함 이슈:
  - Issue 1 `[P0] DB 기반 계층 구축`
  - Issue 2 `[P0] RSS Collector Worker 및 폴링 스케줄 구현`
  - Issue 3 `[P0] 중복 제거 및 정규화 키 구현`
- 종료 조건:
  - DB 마이그레이션 완료
  - RSS 폴링으로 신규 데이터 적재
  - 중복 데이터 재삽입 방지 검증 완료

## Sprint 1 (MVP API 완성, 1주)
- 목표: 상세 파싱 + API 소비 가능 상태 달성
- 포함 이슈:
  - Issue 4 `[P0] 공시 상세 페이지 파서 구현`
  - Issue 5 `[P0] API DB 와이어링 및 API_SPEC 경로 정합`
- 종료 조건:
  - 상세 데이터가 저장되고 조회 가능
  - `/api/v1/disclosures`, `/api/v1/disclosures/{id}`, `/api/v1/categories`, `/api/v1/companies/{company}/disclosures` 동작
  - health 경로 전략 문서/코드 정합 완료

## Sprint 2 (운영 품질 게이트, 1주)
- 목표: 운영/품질 요구사항 충족
- 포함 이슈:
  - Issue 6 `[P0] 운영 최소셋: health/readiness, metrics, 구조화 로그`
  - Issue 7 `[P0] 테스트 기반선 구축`
- 종료 조건:
  - health/readiness/metrics 노출
  - 구조화 로그 확인 가능
  - 핵심 테스트 세트 통과

## Sprint 3 (지능화 MVP+, 1주)
- 목표: 분류/추출/정정 추적까지 MVP 확장
- 포함 이슈:
  - Issue 8 `[P1] 분류 엔진 v0 (Rule-first + AI fallback 인터페이스)`
  - Issue 9 `[P1] 카테고리별 필드 추출 v0`
  - Issue 10 `[P1] 정정공시 추적 및 버전 이력 연결`
- 종료 조건:
  - 분류 결과(category/confidence/evidence) 저장
  - 1~2개 카테고리 필드 추출/저장
  - 정정공시 관계 조회 가능

## 실행 규칙
- 각 Sprint 시작 전: 의존 이슈 완료 여부 확인
- 각 이슈 종료 시: 코드 + 테스트 + 문서 동시 갱신
- 배포 게이트: Sprint 2 종료 전에는 외부 연동용 "안정 버전" 태깅 금지
