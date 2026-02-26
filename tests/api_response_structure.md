# API Response Structure

## GET /api/v1/disclosures

### List Response (Cursor-based Pagination)

```json
{
  "items": [
    {
      "id": 1,
      "company_name": "삼성전자",
      "title": "주식매수보고서",
      "published_at": "2025-01-15T10:00:00",
      "url": "https://example.com/disclosure/1",
      "source": "KIND",
      "reg_date": "2025-01-15",
      "drm": false,
      "classifications": [
        {
          "category": "정기공시",
          "confidence": 1.0,
          "created_at": "2025-01-15T10:05:00"
        }
      ]
    }
  ],
  "count": 10,
  "total": 100,
  "next_cursor": "2025-01-15T10:00:00|1"
}
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| cursor | string | No | null | Cursor for pagination (format: `published_at|id`) |
| limit | integer | No | 50 | Max items per page (1-100) |
| since | string | No | null | Filter by published_at >= since (ISO 8601) |
| category | string | No | null | Filter by classification category |
| company | string | No | null | Filter by company name (partial match) |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| items | array | List of disclosure objects |
| count | integer | Number of items in current page |
| total | integer | Total count of items matching filters |
| next_cursor | string or null | Cursor for next page (null if no more pages) |

---

## GET /api/v1/disclosures/{id}

### Detail Response

```json
{
  "id": 1,
  "company_name": "삼성전자",
  "title": "주식매수보고서",
  "published_at": "2025-01-15T10:00:00",
  "url": "https://example.com/disclosure/1",
  "source": "KIND",
  "reg_date": "2025-01-15",
  "drm": false,
  "body": "공시 본문...",
  "classifications": [
    {
      "category": "정기공시",
      "confidence": 1.0,
      "created_at": "2025-01-15T10:05:00"
    }
  ],
  "extracted_fields": [
    {
      "field_name": "매수기간",
      "field_value": "2025-01-01 ~ 2025-01-15",
      "confidence": 0.95
    }
  ]
}
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| include_body | boolean | No | false | Include body text in response |
| body_max_chars | integer | No | null | Truncate body to max characters (if provided) |

---

## GET /api/v1/categories

### Categories Response

```json
{
  "categories": [
    "정기공시",
    "주요사항보고",
    "공시공고",
    "자율공시",
    "재무정보"
  ]
}
```

---

## GET /health

### Health Check Response

```json
{
  "status": "ok"
}
```
