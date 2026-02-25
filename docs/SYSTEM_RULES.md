# Global System Rules (Mandatory)

These rules are mandatory for all code and documentation.

1. 데이터는 반드시 구조화하여 저장한다 (raw + normalized + derived).
2. API First: 외부 시스템 연동을 위한 명확한 스키마/버전 전략을 가진다.
3. 확장성과 유지보수성을 최우선으로 한다 (모듈화, 테스트, 관측성).
4. AI Agent는 분리된 모듈로 설계하며, 실패 시 deterministic fallback을 제공한다.
5. 네트워크 요청은 레이트리밋/재시도/타임아웃을 기본 적용한다.
6. 하드코딩 금지: URL, interval, DB, key는 config/env로 관리한다.
7. 모든 주요 모듈은 테스트 가능해야 한다 (unit tests 최소).
8. oh-my-opencode 플러그인을 활용하여 반복 구현(스키마/CRUD/테스트)을 표준화한다.
