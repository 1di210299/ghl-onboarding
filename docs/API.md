# API Documentation

Complete API reference for the GHL Healthcare Onboarding System.

## Base URL

**Local:** `http://localhost:8000`  
**Production:** `https://your-api.railway.app`

## Authentication

Currently uses tenant-based authentication. JWT authentication can be added for multi-user access.

---

## Endpoints

### Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

### Onboarding

#### Start Onboarding Session

**POST** `/api/onboarding/start`

Initiates a new onboarding session for a client.

**Request Body:**
```json
{
  "tenant_id": "uuid",
  "practice_name": "Optional Practice Name"
}
```

**Response:**
```json
{
  "session_id": "sess_abc123xyz",
  "client_id": "uuid",
  "message": "Welcome! I'm here to help onboard your practice...",
  "current_step": 0
}
```

#### Send Message

**POST** `/api/onboarding/message`

Send a user message in an active onboarding session.

**Request Body:**
```json
{
  "session_id": "sess_abc123xyz",
  "message": "Healthy Life Medical Center"
}
```

**Response:**
```json
{
  "session_id": "sess_abc123xyz",
  "bot_message": "Great! Is there a legal business name...",
  "current_step": 1,
  "is_completed": false,
  "collected_data": {
    "practice_name": "Healthy Life Medical Center"
  }
}
```

#### Get Onboarding Status

**GET** `/api/onboarding/status/{session_id}`

Get current status of an onboarding session.

**Response:**
```json
{
  "session_id": "sess_abc123xyz",
  "client_id": "uuid",
  "current_step": 5,
  "total_steps": 10,
  "progress_percent": 50,
  "is_completed": false,
  "started_at": "2025-01-15T10:00:00Z",
  "completed_at": null,
  "collected_data": {...}
}
```

---

### Clients

#### List Clients

**GET** `/api/clients`

Get paginated list of clients with optional filtering.

**Query Parameters:**
- `tenant_id` (required): Tenant UUID
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)
- `search` (optional): Search by practice name or email
- `status` (optional): Filter by status (completed, pending)
- `terminology` (optional): Filter by terminology preference

**Response:**
```json
{
  "clients": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

#### Get Client

**GET** `/api/clients/{client_id}`

Get detailed information for a specific client.

**Response:**
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "practice_name": "Healthy Life Medical Center",
  "legal_name": "Healthy Life Medical Center LLC",
  "email": "info@healthylife.com",
  "phone": "(555) 123-4567",
  "address": {
    "street": "123 Medical Plaza Dr",
    "city": "Los Angeles",
    "state": "CA",
    "zip": "90210"
  },
  "social_links": {...},
  "terminology_preference": "patients",
  "brand_colors": {...},
  "business_goals": [...],
  "ghl_contact_id": "ghl_abc123",
  "onboarding_completed": true,
  "onboarding_data": {...},
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:45:00Z"
}
```

#### Update Client

**PATCH** `/api/clients/{client_id}`

Update client information (partial updates supported).

**Request Body:**
```json
{
  "email": "newemail@practice.com",
  "phone": "(555) 987-6543",
  "business_goals": ["New goal 1", "New goal 2"]
}
```

#### Delete Client

**DELETE** `/api/clients/{client_id}`

Delete a client (hard delete).

**Response:** 204 No Content

---

### Webhooks

#### Onboarding Complete

**POST** `/api/webhooks/onboarding-complete`

Triggered when onboarding is completed. Initiates sync to GoHighLevel.

**Request Body:**
```json
{
  "event": "onboarding.completed",
  "client_id": "uuid",
  "tenant_id": "uuid",
  "timestamp": "2025-01-15T10:45:00Z",
  "data": {...}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Onboarding completion webhook processed successfully",
  "client_id": "uuid",
  "ghl_contact_id": "ghl_abc123"
}
```

#### GHL Sync Complete

**POST** `/api/webhooks/ghl-sync-complete`

Called by n8n after GoHighLevel sync completes.

**Request Body:**
```json
{
  "client_id": "uuid",
  "ghl_contact_id": "ghl_abc123"
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Current rate limit: 60 requests per minute per IP address.

Rate limit headers:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

---

## Interactive Documentation

When the API is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.

---

## Code Examples

### Python

```python
import requests

# Start onboarding
response = requests.post(
    "http://localhost:8000/api/onboarding/start",
    json={
        "tenant_id": "00000000-0000-0000-0000-000000000001",
        "practice_name": "Test Practice"
    }
)
session_data = response.json()

# Send message
response = requests.post(
    "http://localhost:8000/api/onboarding/message",
    json={
        "session_id": session_data["session_id"],
        "message": "Healthy Life Medical Center"
    }
)
```

### JavaScript

```javascript
// Start onboarding
const response = await fetch('http://localhost:8000/api/onboarding/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tenant_id: '00000000-0000-0000-0000-000000000001',
    practice_name: 'Test Practice'
  })
});
const sessionData = await response.json();

// Send message
const messageResponse = await fetch('http://localhost:8000/api/onboarding/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: sessionData.session_id,
    message: 'Healthy Life Medical Center'
  })
});
```

### cURL

```bash
# Start onboarding
curl -X POST http://localhost:8000/api/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "00000000-0000-0000-0000-000000000001",
    "practice_name": "Test Practice"
  }'

# Send message
curl -X POST http://localhost:8000/api/onboarding/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123xyz",
    "message": "Healthy Life Medical Center"
  }'
```
