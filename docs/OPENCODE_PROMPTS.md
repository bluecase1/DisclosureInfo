# OpenCode Prompt Pack

## 1) Repo onboarding
- "docs/SYSTEM_RULES.md와 docs/PROJECT.md를 기준으로 현재 레포 코드를 스캔해서 아키텍처를 정리하고, 부족한 모듈/폴더 구조를 제안해줘."

## 2) MVP plan
- "docs/RSS_SPEC.md와 docs/API_SPEC.md 기준으로 MVP 구현 계획(티켓 단위)과 각 티켓의 파일 변경 리스트를 만들어줘."

## 3) Collector implementation
- "RSS_URL을 폴링하여 신규 항목을 DB에 저장하는 collector worker를 설계/구현해줘. tenacity로 재시도, 중복제거 포함."

## 4) Parsing
- "공시 상세 페이지를 가져와 제목/본문 텍스트/회사 정보를 파싱하는 parser 모듈을 만들어줘."

## 5) AI agent stubs
- "docs/AI_AGENT_DESIGN.md 기준으로 classification/extraction agent 인터페이스와 더미 구현체를 만들어줘(추후 LLM 연결)."

## 6) API wiring
- "SQLAlchemy 모델과 Pydantic schema를 작성하고 /api/v1/disclosures가 DB 결과를 반환하게 연결해줘."

## 7) Tests
- "핵심 로직(중복제거/분류 규칙/파싱)을 pytest로 테스트 추가해줘."
