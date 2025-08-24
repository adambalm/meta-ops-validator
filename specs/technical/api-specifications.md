# MetaOps Validator MVP API Specification

## Overview
REST API for ONIX file validation with sales impact scoring and retailer compliance checking. Built for enterprise publishers to validate metadata quality before distribution.

## Core Endpoints (MVP)

### 1. File Validation
```
POST /api/v1/validate
Content-Type: multipart/form-data
Authorization: Bearer {jwt_token}

Body:
- file: ONIX XML file (required)
- profile: validation profile (optional, default: "standard")
  - "standard": XSD + Schematron + Basic Rules
  - "retailer": Include retailer-specific compliance
  - "nielsen": Include Nielsen completeness scoring

Response (200 OK):
{
  "validation_id": "val_123456789",
  "status": "processing",
  "estimated_completion": "2025-01-15T10:30:00Z",
  "validation_url": "/api/v1/validation/{validation_id}"
}

Errors:
- 400: Invalid file format or size > 50MB
- 401: Invalid/expired token
- 429: Rate limit exceeded
```

### 2. Validation Status
```
GET /api/v1/validation/{validation_id}
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "validation_id": "val_123456789",
  "status": "completed",  // "processing", "completed", "failed"
  "created_at": "2025-01-15T10:25:00Z",
  "completed_at": "2025-01-15T10:25:45Z",
  "file_info": {
    "filename": "catalog_2025Q1.xml",
    "size_bytes": 2458627,
    "title_count": 1247
  },
  "results_summary": {
    "total_errors": 23,
    "total_warnings": 156,
    "nielsen_completeness": 78.5,
    "retailer_compliance": {
      "amazon": 85.2,
      "barnes_noble": 72.1,
      "ingram": 91.7
    }
  }
}

Errors:
- 404: Validation ID not found
- 401: Unauthorized access
```

### 3. Detailed Results
```
GET /api/v1/validation/{validation_id}/results
Authorization: Bearer {jwt_token}
Query Parameters:
- level: "error", "warning", "info" (filter by severity)
- domain: "xsd", "schematron", "rules" (filter by validation type)
- limit: max results (default: 100, max: 1000)
- offset: pagination offset

Response (200 OK):
{
  "validation_id": "val_123456789",
  "total_issues": 179,
  "filtered_count": 23,
  "issues": [
    {
      "line": 1247,
      "level": "error",
      "domain": "xsd", 
      "type": "missing_element",
      "message": "Required element 'ProductIDType' missing",
      "path": "Product[234]/ProductIdentifier",
      "sales_impact": "high",
      "affected_retailers": ["amazon", "barnes_noble"]
    }
  ],
  "nielsen_details": {
    "completeness_score": 78.5,
    "missing_fields": ["BISACMainSubject", "Audience"],
    "field_scores": {
      "title": 100.0,
      "isbn": 98.2,
      "price": 45.8
    }
  }
}
```

### 4. Multi-Retailer Validation
```
POST /api/v1/validate/retailers
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

Body:
- file: ONIX XML file
- retailers[]: array of retailer codes
  - "amazon", "barnes_noble", "ingram", "baker_taylor"

Response (200 OK):
{
  "validation_id": "val_123456789",
  "retailer_profiles": ["amazon", "barnes_noble", "ingram"],
  "status": "processing",
  "validation_url": "/api/v1/validation/{validation_id}"
}
```

### 5. Health Check
```
GET /api/v1/health

Response (200 OK):
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "2d 4h 32m",
  "services": {
    "validator": "healthy",
    "database": "healthy"
  }
}
```

## Authentication

**JWT Bearer Tokens**
```
POST /api/v1/auth/token
Content-Type: application/json

Body:
{
  "api_key": "pk_live_abc123...",
  "api_secret": "sk_live_def456..."
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Rate Limiting

| Tier | Requests/Hour | File Size Limit | Concurrent Validations |
|------|---------------|------------------|----------------------|
| Starter | 50 | 10MB | 1 |
| Professional | 500 | 50MB | 5 |
| Enterprise | 2000 | 200MB | 20 |

Rate limit headers included in all responses:
```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 347
X-RateLimit-Reset: 1642694400
```

## Error Handling

**Standard HTTP Status Codes:**
- 200: Success
- 400: Bad Request (invalid file, missing parameters)
- 401: Unauthorized (invalid/missing token)
- 404: Resource not found
- 413: Payload too large
- 422: Unprocessable entity (valid format, invalid content)
- 429: Too many requests
- 500: Internal server error

**Error Response Format:**
```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "File must be valid XML with ONIX structure",
    "details": "Root element 'ONIXMessage' not found",
    "timestamp": "2025-01-15T10:25:00Z"
  }
}
```

## Technical Notes

- All timestamps in ISO 8601 UTC format
- File uploads processed asynchronously (>5MB files)
- Results cached for 30 days
- WebSocket endpoint for real-time status updates (future)
- All scores tagged as [verified] or [inference] per data ethics policy
- Namespace-aware validation for production ONIX files