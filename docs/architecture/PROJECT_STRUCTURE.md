# Project Structure

```
ghl-onboarding/
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
├── DEPLOYMENT.md                  # Deployment guide
├── API.md                         # API documentation
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment variables template
├── docker-compose.yml             # Docker Compose for local development
│
├── backend/                       # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application entry point
│   │   │
│   │   ├── api/                  # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── clients.py        # Client management endpoints
│   │   │   ├── onboarding.py     # Onboarding conversation endpoints
│   │   │   └── webhooks.py       # Webhook endpoints
│   │   │
│   │   ├── core/                 # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # Settings and environment variables
│   │   │   └── database.py       # Supabase client configuration
│   │   │
│   │   ├── models/               # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── client.py         # Client data models
│   │   │   └── onboarding.py     # Onboarding API models
│   │   │
│   │   └── services/             # Business logic
│   │       ├── __init__.py
│   │       ├── state.py          # LangGraph state definitions
│   │       ├── validators.py     # Data validation functions
│   │       └── workflow.py       # LangGraph conversation workflow
│   │
│   ├── tests/                    # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py          # Test configuration
│   │   └── test_models.py       # Model tests
│   │
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Docker configuration
│   └── railway.toml             # Railway deployment config
│
├── frontend/                     # Next.js Dashboard
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Home page (redirects)
│   │   ├── providers.tsx        # React Query provider
│   │   ├── globals.css          # Global styles
│   │   │
│   │   └── dashboard/           # Dashboard pages
│   │       ├── page.tsx         # Dashboard overview
│   │       └── clients/
│   │           └── [id]/
│   │               └── page.tsx # Client detail page
│   │
│   ├── components/              # React components
│   │   ├── ui/
│   │   │   └── button.tsx      # shadcn button component
│   │   ├── client-card.tsx     # Client information card
│   │   ├── clients-table.tsx   # Clients table with sorting
│   │   ├── conversation-history.tsx  # Chat history display
│   │   └── search-bar.tsx      # Search with debouncing
│   │
│   ├── lib/                     # Utilities
│   │   ├── api.ts              # API client
│   │   ├── supabase.ts         # Supabase client
│   │   └── utils.ts            # Helper functions
│   │
│   ├── package.json             # Node dependencies
│   ├── tsconfig.json            # TypeScript config
│   ├── tailwind.config.ts       # Tailwind CSS config
│   ├── postcss.config.js        # PostCSS config
│   ├── next.config.js           # Next.js config
│   ├── Dockerfile              # Docker configuration
│   └── vercel.json             # Vercel deployment config
│
├── database/                    # Database migrations
│   └── migrations/
│       └── 001_initial_schema.sql  # Initial schema with RLS
│
├── n8n/                         # n8n Workflows
│   ├── workflows/
│   │   └── onboarding-to-ghl-sync.json  # GHL sync workflow
│   └── README.md               # n8n setup guide
│
└── .github/                     # GitHub Actions
    └── workflows/
        └── ci-cd.yml           # CI/CD pipeline
```

## Key Files Overview

### Backend Core Files

1. **app/main.py**
   - FastAPI application initialization
   - CORS middleware configuration
   - Router inclusion
   - Global exception handler

2. **app/core/config.py**
   - Environment variables management
   - Application settings
   - Pydantic Settings for type safety

3. **app/core/database.py**
   - Supabase client initialization
   - Connection management
   - RLS context setting

4. **app/services/workflow.py**
   - LangGraph conversation state machine
   - Question flow management
   - Response validation
   - Data persistence

5. **app/models/client.py**
   - Pydantic models for client data
   - Validation logic for all fields
   - Type definitions

### Frontend Core Files

1. **app/layout.tsx**
   - Root layout with providers
   - Global styles import
   - Font configuration

2. **app/dashboard/page.tsx**
   - Main dashboard view
   - Client list with filtering
   - Search and export functionality

3. **lib/supabase.ts**
   - Supabase client configuration
   - TypeScript types for database

4. **lib/api.ts**
   - API client wrapper
   - Request/response handling
   - Type-safe endpoints

5. **components/clients-table.tsx**
   - Responsive table component
   - Sorting and filtering
   - Row actions

### Database

1. **database/migrations/001_initial_schema.sql**
   - Complete schema definition
   - Row-Level Security policies
   - Indexes and constraints
   - Helper functions
   - Sample data

### Automation

1. **n8n/workflows/onboarding-to-ghl-sync.json**
   - Webhook trigger
   - Field mapping
   - GoHighLevel API integration
   - Error handling
   - Backend notification

### Deployment

1. **docker-compose.yml**
   - Multi-container local setup
   - Backend + Frontend + n8n
   - Volume management
   - Network configuration

2. **Dockerfile** (Backend)
   - Python 3.11 image
   - Dependency installation
   - Non-root user
   - Health checks

3. **Dockerfile** (Frontend)
   - Multi-stage build
   - Node.js 20 image
   - Production optimization
   - Health checks

4. **railway.toml**
   - Railway deployment config
   - Build commands
   - Start commands
   - Health check paths

5. **vercel.json**
   - Vercel deployment config
   - Environment variable mappings
   - Framework detection

## Technology Stack Summary

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **AI/ML:** LangChain, LangGraph, OpenAI GPT-4o
- **Database:** Supabase (PostgreSQL)
- **Validation:** Pydantic v2
- **HTTP Client:** httpx, aiohttp

### Frontend
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **State Management:** React Query (@tanstack/react-query)
- **Database Client:** Supabase JS

### Automation
- **Platform:** n8n
- **Integration:** GoHighLevel API
- **Trigger:** Webhooks

### Infrastructure
- **Database:** Supabase (managed PostgreSQL)
- **Backend Hosting:** Railway / Render
- **Frontend Hosting:** Vercel
- **Automation:** n8n Cloud / Self-hosted
- **Containers:** Docker + Docker Compose

### DevOps
- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions
- **Testing:** pytest (backend), Jest (frontend)
- **Type Checking:** mypy (backend), TypeScript (frontend)
- **Linting:** pylint, ESLint

## File Counts by Type

- **Python Files:** 15+
- **TypeScript/React Files:** 20+
- **Configuration Files:** 10+
- **Documentation Files:** 5
- **SQL Files:** 1 (migration)
- **JSON Files:** 3 (n8n, configs)
- **Docker Files:** 3

## Total Lines of Code (Approximate)

- **Backend:** ~3,500 lines
- **Frontend:** ~2,000 lines
- **Database:** ~500 lines
- **Configuration:** ~500 lines
- **Documentation:** ~2,000 lines
- **Total:** ~8,500 lines

## Dependencies

### Backend (requirements.txt)
- 25+ Python packages
- Main: FastAPI, LangChain, Supabase, OpenAI

### Frontend (package.json)
- 15+ npm packages
- Main: Next.js, React, Supabase, TanStack Query

## Key Features Implementation

### 1. Conversational Onboarding
- **Files:** `workflow.py`, `state.py`, `validators.py`
- **Lines:** ~1,200
- **Components:** LangGraph state machine, OpenAI GPT-4o, validation

### 2. Database with RLS
- **Files:** `001_initial_schema.sql`, `database.py`
- **Lines:** ~500
- **Features:** Multi-tenant, RLS policies, indexes

### 3. GoHighLevel Integration
- **Files:** `onboarding-to-ghl-sync.json`, `webhooks.py`
- **Lines:** ~400
- **Features:** Field mapping, error handling, retry logic

### 4. Team Dashboard
- **Files:** Multiple React components
- **Lines:** ~1,500
- **Features:** Search, filter, export, detail views

## Development Workflow

1. **Setup:** Follow QUICKSTART.md
2. **Development:** Use docker-compose for local environment
3. **Testing:** pytest for backend, manual testing for frontend
4. **Deployment:** Follow DEPLOYMENT.md
5. **Monitoring:** Use platform dashboards

## Maintenance

- **Database:** Automatic backups via Supabase
- **Code:** Version controlled via Git
- **Updates:** Dependency updates via Dependabot
- **Monitoring:** Built-in platform monitoring

## Security Features

- Row-Level Security (RLS) on all tables
- Environment variables for secrets
- HTTPS enforced in production
- CORS restrictions
- Input validation on all endpoints
- JWT authentication ready

## Scalability

- Horizontal scaling via platform (Railway/Vercel)
- Database connection pooling
- CDN for frontend assets
- API rate limiting
- Caching with React Query

## Future Enhancements

Potential additions:
- [ ] Multi-tenant authentication
- [ ] Real-time chat via WebSockets
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] Mobile app
- [ ] Bulk import/export
- [ ] Custom branding per tenant
- [ ] API rate limiting per tenant
- [ ] Advanced search with Algolia
- [ ] Audit logs
