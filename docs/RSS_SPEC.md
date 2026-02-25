# RSS Data Specification

## RSS Source
http://kind.krx.co.kr:80/disclosure/rsstodaydistribute.do?method=searchRssTodayDistribute&repIsuSrtCd=&mktTpCd=0&searchCorpName=&currentPageSize=15

## Data Flow
1. RSS Fetch (XML)
2. Parse items (guid/title/link/pubDate/description 등)
3. Normalize & deduplicate (guid/link 기반)
4. Fetch disclosure detail (link) and extract:
   - title
   - published_at
   - company name / code if available
   - body text (가능한 범위)
   - attachments metadata (가능한 범위)
5. Store raw + normalized data
6. Classify category + extract required fields
7. Serve via API

## Polling Strategy (Default)
- Interval: 5~10 minutes (configurable)
- Retry: exponential backoff + jitter
- Timeout: 10s~20s (configurable)
- User-Agent: 명시, 과도한 요청 금지

## Quality / Robustness Considerations
- 중복 공시 제거 (guid/link + hash)
- 정정공시 추적 (원공시 참조/제목 패턴/본문 단서)
- 장애/일시적 차단 대응 (재시도, circuit breaker)
- 데이터 정합성 (필수 필드 누락 시 validation agent로 보완)

## Missing Capabilities To Consider (Backlog)
- 중요도 스코어링 (계약금액/이익 영향/지분율 변동 등)
- 기업별 타임라인/히스토리
- 요약(한 줄/3줄) + 키포인트 추출
- 이벤트 알림(Webhook/Slack/Email)
