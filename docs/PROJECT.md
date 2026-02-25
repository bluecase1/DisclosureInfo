# DisclosureInfo Project

## Goal
KIND 공시 RSS 피드를 수집, 분석, 분류하여 구조화된 데이터로 가공하고 외부 시스템에 API 형태로 제공하는 서비스 구축.

## Target Repository
https://github.com/bluecase1/DisclosureInfo.git

## Core Objectives
1. KIND RSS 실시간 수집(스케줄러/워커)
2. 전체 공시 내용 수집(상세 페이지/본문 포함)
3. 자동 카테고리 분류(규칙 + AI Agent)
4. 카테고리별 필수 필드 추출/정규화
5. 외부 시스템 연동 API 제공(API First)
6. 운영 관점의 관측/재시도/중복제거/정정 추적

## Service Type
- 지속 운영 가능한 서버형 서비스
- 확장 가능한 아키텍처(Worker 수평 확장)
- 솔루션 패키지화 가능 구조(컨테이너/설정 기반)

## Non-Goals (초기 범위에서 제외)
- 실시간 트레이딩/주문 연동
- 개인화 추천, 투자자문 기능

## Key Constraints / Assumptions
- 공시 수집은 KIND RSS를 기본 진입점으로 사용
- 상세 본문/첨부 수집은 합법적/기술적으로 가능한 범위에서 수행(robots/접근정책 준수)
- 외부 시스템 제공은 REST API를 기본으로 하고, 추후 Webhook/Message Bus 확장

## Definition of Done (MVP)
- RSS 폴링 → 신규 항목 적재(중복 제거)
- 공시 상세 내용 파싱(최소: 제목/본문 텍스트/링크/일시/회사 식별)
- 카테고리 분류 + 확신도
- 카테고리별 필수 필드 최소 1~2개 카테고리에서 추출
- API: 목록/상세/카테고리 조회
- 기본 모니터링(health, metrics/log), 실패 재시도
