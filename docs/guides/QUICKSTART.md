# Quick Start Guide

This guide will help you get the GHL Healthcare Onboarding System running locally in under 10 minutes.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Supabase account (free tier works)
- OpenAI API key

## Step 1: Clone and Setup

```bash
cd ghl-onboarding
```

## Step 2: Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your keys:
# - OPENAI_API_KEY (from OpenAI)
# - SUPABASE_URL (from Supabase dashboard)
# - SUPABASE_ANON_KEY (from Supabase dashboard)
# - SUPABASE_SERVICE_KEY (from Supabase dashboard)
# - DATABASE_URL (from Supabase dashboard)
# - N8N_WEBHOOK_URL (leave default for now)
# - JWT_SECRET (generate a random string)
```

## Step 3: Setup Database

1. Go to https://supabase.com and create a new project
2. Open SQL Editor
3. Copy and paste the entire content from `database/migrations/001_initial_schema.sql`
4. Click "Run" to execute the migration
5. Verify tables are created in the Table Editor

## Step 4: Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

Test it: http://localhost:8000/health

## Step 5: Start Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp ../.env.example .env.local

# Edit .env.local with your Supabase credentials

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Step 6: Test the System

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Start onboarding
curl -X POST http://localhost:8000/api/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "00000000-0000-0000-0000-000000000001",
    "practice_name": "Test Practice"
  }'
```

### Test Dashboard

1. Open http://localhost:3000
2. You should be redirected to /dashboard
3. You should see the demo client from the migration

## Step 7: (Optional) Setup n8n

For local testing without GoHighLevel sync:

```bash
# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=admin \
  n8nio/n8n
```

Access n8n at http://localhost:5678

## Common Issues

### Backend won't start
- Check Python version: `python --version` (should be 3.11+)
- Activate virtual environment
- Check all environment variables are set

### Frontend won't start
- Check Node version: `node --version` (should be 20+)
- Delete node_modules and run `npm install` again
- Check .env.local exists with correct values

### Database connection failed
- Verify Supabase credentials in .env
- Check if Supabase project is active
- Verify migration ran successfully

### Can't see data in dashboard
- Check browser console for errors
- Verify NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local
- Check Supabase Table Editor to confirm data exists

## Next Steps

Once everything is running:

1. ✅ Test the onboarding flow via API
2. ✅ Create a new client in the dashboard
3. ✅ Configure n8n workflows
4. ✅ Set up GoHighLevel integration
5. ✅ Deploy to production (see DEPLOYMENT.md)

## Development Tips

- Backend automatically reloads on file changes (--reload flag)
- Frontend hot-reloads automatically
- Check logs in terminal for errors
- Use Swagger docs at http://localhost:8000/docs for API testing

## Support

If you encounter issues:

1. Check the logs in your terminal
2. Review the error messages carefully
3. Verify all environment variables are set correctly
4. Check the database migration ran successfully
5. Refer to the full README.md for detailed documentation

---

**You're all set!** The system is now running locally. Start testing the onboarding flow and explore the dashboard.
