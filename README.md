# DisclosureInfo

KIND 공시 RSS를 수집/분석/분류하여 외부 시스템에 API로 제공하는 서비스.

## Documentation
See `docs/`:
- PROJECT.md: 목표/범위
- RSS_SPEC.md: RSS 수집/파싱 스펙
- CATEGORY_POLICY.md: 분류/필드 정책
- AI_AGENT_DESIGN.md: 에이전트 설계
- ARCHITECTURE.md: 아키텍처
- API_SPEC.md: API 스펙
- SYSTEM_RULES.md: 강제 규칙
- OH_MY_OPENCODE.md: 플러그인 활용

## Quickstart (dev)
```bash
docker compose up --build
```

## Environment Variables
런타임 설정은 하드코딩하지 않고 환경 변수로 관리한다.

1. 예시 파일 복사
```bash
cp .env.example .env
```

2. 필요 시 값 수정
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `RSS_URL`: KIND RSS 소스 URL
- `POLL_INTERVAL_SECONDS`: RSS 폴링 주기(초)
- `LOG_LEVEL`: 로그 레벨

`docker-compose.yml`은 위 환경 변수를 우선 사용하고, 미지정 시 기본값을 사용한다.

API: http://localhost:8000/docs
