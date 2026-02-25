# API Specification (v0)

## Base Path
/api/v1

## Endpoints

### GET /health
- 서비스 상태 확인

### GET /disclosures
- Query:
  - since: ISO datetime (optional)
  - category: enum (optional)
  - company: string (optional)
  - limit: int (default 50, max 200)
- Returns: disclosure list

### GET /disclosures/{id}
- Returns: disclosure + detail + classification + extracted fields (if available)

### GET /categories
- Returns: supported categories

### GET /companies/{company}/disclosures
- company: name or code (future)
- Returns: recent disclosures

## Future Extensions
- Webhook registration
- Full-text search
- Importance score filtering
