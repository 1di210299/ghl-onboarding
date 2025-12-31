# GHL Healthcare Onboarding System - Deployment Guide

## Overview

This guide covers deploying the complete system to production using:
- **Vercel** for Next.js frontend
- **Railway** for FastAPI backend
- **Supabase** for database (managed)
- **n8n Cloud** or self-hosted for automation

## Prerequisites

- [ ] Supabase account with project created
- [ ] Vercel account
- [ ] Railway account (or Render)
- [ ] n8n Cloud account (or Docker host)
- [ ] OpenAI API key
- [ ] GoHighLevel API access

---

## Part 1: Database Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to https://supabase.com
2. Create new project
3. Note down:
   - Project URL
   - Anon/Public key
   - Service role key
   - Database password

### 1.2 Run Migrations

1. Open SQL Editor in Supabase dashboard
2. Copy content from `database/migrations/001_initial_schema.sql`
3. Execute the migration
4. Verify tables are created:
   - `tenants`
   - `clients`

### 1.3 Configure Row-Level Security

RLS policies are included in the migration and should be automatically enabled.

---

## Part 2: Backend Deployment (Railway)

### 2.1 Connect Repository

1. Go to https://railway.app
2. Create new project
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Set root directory to `/backend`

### 2.2 Configure Environment Variables

In Railway dashboard, add these variables:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# n8n
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/onboarding-complete

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### 2.3 Deploy

1. Railway will automatically deploy
2. Note the generated URL: `https://your-app.railway.app`
3. Test health endpoint: `https://your-app.railway.app/health`

### 2.4 Alternative: Render

If using Render instead:

1. Create new Web Service
2. Connect repository
3. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (same as Railway)

---

## Part 3: Frontend Deployment (Vercel)

### 3.1 Connect Repository

1. Go to https://vercel.com
2. Import project from Git
3. Select your repository
4. Set root directory to `/frontend`

### 3.2 Configure Environment Variables

Add in Vercel dashboard:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

### 3.3 Deploy

1. Vercel will automatically build and deploy
2. Your dashboard will be available at: `https://your-project.vercel.app`
3. Custom domain can be added in Vercel settings

---

## Part 4: n8n Automation Setup

### Option A: n8n Cloud (Recommended)

1. Sign up at https://n8n.io/cloud
2. Create new workflow
3. Import `n8n/workflows/onboarding-to-ghl-sync.json`
4. Configure credentials:
   - GoHighLevel OAuth2
   - HTTP Request (for backend)
5. Set environment variables:
   - `GHL_LOCATION_ID`
   - `GHL_WORKFLOW_ID`
   - `BACKEND_API_URL`
6. Activate workflow
7. Copy webhook URL
8. Update Railway environment variable: `N8N_WEBHOOK_URL`

### Option B: Self-Hosted n8n

1. Deploy n8n using Docker:

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=your-password \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

2. Access at http://your-server:5678
3. Import and configure workflow as above
4. Set up reverse proxy with SSL (Nginx/Caddy)

---

## Part 5: GoHighLevel Configuration

### 5.1 Create Custom Fields

In GoHighLevel, create these custom fields for contacts:

| Field Name | Type | Key |
|------------|------|-----|
| Practice Name | Text | practice_name |
| Legal Name | Text | legal_name |
| Terminology | Dropdown | terminology_preference |
| Brand Colors | Text | brand_colors |
| Business Goals | Text | business_goals |
| Facebook | URL | social_facebook |
| Instagram | URL | social_instagram |
| LinkedIn | URL | social_linkedin |
| Twitter | URL | social_twitter |
| Onboarding Completed | Date | onboarding_completed_at |

### 5.2 Create Workflow (Optional)

Create a GHL workflow that triggers when contacts are added via API:
1. Send welcome email
2. Assign to team member
3. Create follow-up tasks

### 5.3 Get API Credentials

1. Go to GHL Settings > API Keys
2. Create new API key
3. Note Location ID
4. Note Workflow ID (if using automated workflows)

---

## Part 6: Domain & SSL Configuration

### 6.1 Custom Domains

**Frontend (Vercel):**
1. Go to Project Settings > Domains
2. Add custom domain: `dashboard.yourdomain.com`
3. Configure DNS (CNAME or A record)

**Backend (Railway):**
1. Go to Settings > Domains
2. Add custom domain: `api.yourdomain.com`
3. Configure DNS

**n8n:**
1. Set up reverse proxy with Nginx/Caddy
2. Configure SSL with Let's Encrypt
3. Point subdomain: `n8n.yourdomain.com`

### 6.2 SSL Certificates

All platforms (Vercel, Railway, Supabase) provide automatic SSL.

For self-hosted n8n, use Certbot:

```bash
sudo certbot --nginx -d n8n.yourdomain.com
```

---

## Part 7: Monitoring & Logging

### 7.1 Backend Monitoring

Railway/Render provide built-in:
- Logs viewing
- Resource usage
- Uptime monitoring

Add external monitoring:
- Sentry for error tracking
- LogRocket for session replay
- Better Stack for uptime monitoring

### 7.2 Frontend Monitoring

Vercel provides:
- Analytics
- Speed Insights
- Error tracking

### 7.3 Database Monitoring

Supabase dashboard shows:
- Query performance
- Connection pooling
- Storage usage

---

## Part 8: Testing Production

### 8.1 Health Checks

```bash
# Backend
curl https://api.yourdomain.com/health

# Frontend
curl https://dashboard.yourdomain.com

# n8n
curl https://n8n.yourdomain.com/healthz
```

### 8.2 Test Onboarding Flow

1. Start onboarding:
```bash
curl -X POST https://api.yourdomain.com/api/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "your-tenant-id",
    "practice_name": "Test Practice"
  }'
```

2. Complete conversation
3. Verify in dashboard
4. Check GoHighLevel for synced contact

---

## Part 9: Backup & Recovery

### 9.1 Database Backups

Supabase automatically backs up:
- Daily backups (retained 7 days on free tier)
- Point-in-time recovery on paid plans

Manual backup:
```bash
pg_dump $DATABASE_URL > backup.sql
```

### 9.2 Code Backups

- GitHub repository (primary)
- Git tags for releases
- Railway/Vercel deployment history

---

## Part 10: Scaling Considerations

### 10.1 Backend Scaling

Railway:
- Auto-scales based on traffic
- Upgrade plan for more resources
- Add Redis for session management at scale

### 10.2 Database Scaling

Supabase:
- Connection pooling enabled by default
- Upgrade plan for more connections
- Add read replicas if needed

### 10.3 Frontend Scaling

Vercel:
- Automatically scales globally
- Edge caching included
- ISR for better performance

---

## Cost Estimates

### Free Tier (Development)
- Supabase: Free (up to 500MB database)
- Vercel: Free (hobby plan)
- Railway: $5/month credit
- n8n Cloud: Free (5 workflows)
- **Total: ~$5-10/month**

### Production (Small Scale)
- Supabase Pro: $25/month
- Vercel Pro: $20/month
- Railway: $20-50/month
- n8n Cloud Starter: $20/month
- **Total: ~$85-115/month**

### Production (Medium Scale)
- Supabase Pro: $25/month
- Vercel Pro: $20/month
- Railway: $100/month
- n8n Cloud Pro: $50/month
- Monitoring tools: $30/month
- **Total: ~$225/month**

---

## Troubleshooting

### Common Issues

1. **CORS errors:** Update CORS origins in backend config
2. **Database connection failed:** Check connection string and firewall rules
3. **n8n webhook not triggering:** Verify URL and test with curl
4. **OpenAI rate limits:** Implement rate limiting and queuing
5. **Build failures:** Check logs for missing environment variables

### Support Resources

- [Supabase Docs](https://supabase.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [n8n Docs](https://docs.n8n.io)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)

---

## Security Checklist

- [ ] All API keys stored as environment variables
- [ ] Row-Level Security enabled on database
- [ ] HTTPS enforced on all endpoints
- [ ] Rate limiting configured
- [ ] CORS properly restricted
- [ ] JWT secrets are strong and unique
- [ ] Database passwords are strong
- [ ] Backup strategy implemented
- [ ] Monitoring and alerts configured
- [ ] Error messages don't leak sensitive data

---

## Maintenance Tasks

### Weekly
- [ ] Review error logs
- [ ] Check uptime metrics
- [ ] Monitor API usage

### Monthly
- [ ] Review and optimize database queries
- [ ] Check for dependency updates
- [ ] Review cost and usage
- [ ] Backup important data manually

### Quarterly
- [ ] Security audit
- [ ] Performance optimization
- [ ] Capacity planning review
- [ ] Update documentation
