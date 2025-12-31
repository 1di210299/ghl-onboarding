# n8n Workflow Configuration Guide

## Setup Instructions

### 1. Install n8n

```bash
npm install -g n8n
# or with Docker
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### 2. Configure GoHighLevel OAuth2

1. Go to GoHighLevel App Marketplace
2. Create a new OAuth2 application
3. Set redirect URI: `https://your-n8n-instance.com/rest/oauth2-credential/callback`
4. Copy Client ID and Client Secret
5. In n8n:
   - Go to Credentials > New
   - Select "GoHighLevel OAuth2 API"
   - Enter Client ID and Client Secret
   - Authorize the app

### 3. Environment Variables

Add these to your n8n environment:

```bash
# GoHighLevel Configuration
GHL_LOCATION_ID=your-ghl-location-id
GHL_WORKFLOW_ID=your-ghl-workflow-id

# Backend API
BACKEND_API_URL=https://your-backend-api.com
```

### 4. Import Workflows

1. Open n8n interface (http://localhost:5678)
2. Go to Workflows > Import
3. Upload `onboarding-to-ghl-sync.json`
4. Configure credentials for each node
5. Activate the workflow

### 5. Field Mapping

GoHighLevel Custom Fields to create:

| Field Name | Type | Description |
|------------|------|-------------|
| practice_name | Text | Practice display name |
| legal_name | Text | Legal business name |
| terminology_preference | Dropdown | patients/members/clients |
| brand_colors | Text | JSON string of colors |
| business_goals | Text | JSON array of goals |
| social_facebook | URL | Facebook page URL |
| social_instagram | URL | Instagram profile URL |
| social_linkedin | URL | LinkedIn page URL |
| social_twitter | URL | Twitter profile URL |
| onboarding_completed_at | DateTime | Completion timestamp |

### 6. Webhook URL

After activating the workflow, n8n will provide a webhook URL:

```
https://your-n8n-instance.com/webhook/onboarding-complete
```

Add this URL to your backend `.env` file as `N8N_WEBHOOK_URL`.

### 7. Error Handling

The workflow includes error handling that:
- Logs failed sync attempts
- Returns error details to backend
- Can trigger notification workflows

### 8. Rate Limiting

GoHighLevel API has rate limits:
- 50 requests per second
- 5000 requests per hour

The workflow includes built-in retry logic with exponential backoff.

### 9. Testing

Test the workflow with a sample payload:

```bash
curl -X POST https://your-n8n-instance.com/webhook/onboarding-complete \
  -H "Content-Type: application/json" \
  -d '{
    "event": "onboarding.completed",
    "data": {
      "id": "client-uuid",
      "practice_name": "Test Practice",
      "email": "test@practice.com",
      "phone": "(555) 123-4567",
      "address": {
        "street": "123 Main St",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90210"
      }
    }
  }'
```

### 10. Monitoring

Monitor workflow executions:
- n8n Dashboard > Executions
- Check for failed runs
- Review error logs
- Set up alerts for failures

## Troubleshooting

### Common Issues

1. **OAuth2 Authentication Failed**
   - Re-authorize the GoHighLevel credential
   - Check client ID and secret
   - Verify redirect URI

2. **Contact Already Exists**
   - Modify workflow to check for existing contacts
   - Update instead of create if exists
   - Use email as unique identifier

3. **Custom Fields Not Syncing**
   - Verify custom field IDs in GoHighLevel
   - Check field type compatibility
   - Ensure proper JSON formatting

4. **Webhook Not Triggering**
   - Verify webhook URL is correct
   - Check network connectivity
   - Review backend logs for webhook calls

5. **Rate Limit Errors**
   - Implement queue system
   - Add delays between requests
   - Batch process when possible
