# GHL Healthcare Onboarding System - Phase 1

AI-powered client onboarding system for GoHighLevel agencies working with healthcare practices.

## Features

- 🤖 Conversational AI onboarding bot (LangGraph + GPT-4o)
- 🔒 Secure multi-tenant database (Supabase with RLS)
- 🔄 Automatic GoHighLevel sync (n8n workflows)
- 📊 Team dashboard with search (Next.js + shadcn/ui)

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- LangChain + LangGraph
- OpenAI GPT-4o
- Supabase (PostgreSQL)

**Frontend:**
- Next.js 15
- TypeScript
- shadcn/ui
- React Query

**Automation:**
- n8n for webhooks

## Project Structure

```
ghl-onboarding/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js dashboard
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── database/              # Supabase migrations
│   └── migrations/
├── n8n/                   # n8n workflows
│   └── workflows/
└── docker-compose.yml
```

## Setup Instructions

### 1. Database Setup

```bash
# Run migrations in Supabase SQL Editor
cd database/migrations
# Execute 001_initial_schema.sql
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp ../.env.example .env.local
# Edit .env.local with your credentials
npm run dev
```

### 4. n8n Setup

1. Import workflows from `n8n/workflows/`
2. Configure GoHighLevel OAuth2 credentials
3. Update webhook URLs in backend .env

## Environment Variables

See `.env.example` for all required configuration.

## Deployment

### Backend (Railway/Render)
- Push to GitHub
- Connect repository to Railway/Render
- Add environment variables
- Deploy automatically

### Frontend (Vercel)
- Connect repository to Vercel
- Add environment variables
- Deploy automatically

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Security

- Row-Level Security (RLS) enabled on all tables
- JWT authentication for API endpoints
- CORS configured for frontend only
- Environment variables for sensitive data
- Rate limiting on public endpoints

## Development

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test

# Run type checking
npm run type-check
```

## License

MIT
