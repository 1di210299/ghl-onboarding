# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTIONS                                   │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌──────────────────┐          ┌──────────────────┐
        │  TEAM DASHBOARD  │          │  ONBOARDING BOT  │
        │   (Next.js 15)   │          │   (API Client)   │
        │                  │          │                  │
        │  • Client List   │          │  • Start Session │
        │  • Search/Filter │          │  • Send Messages │
        │  • Client Detail │          │  • View Progress │
        │  • Export CSV    │          │                  │
        └──────────┬───────┘          └──────────┬───────┘
                   │                             │
                   │    ┌────────────────────────┘
                   │    │
                   │    │  HTTP Requests
                   │    │
                   ▼    ▼
        ┌────────────────────────────────────┐
        │      BACKEND API (FastAPI)         │
        │                                    │
        │  ┌──────────────────────────────┐ │
        │  │  API Endpoints               │ │
        │  │  • /api/onboarding/start     │ │
        │  │  • /api/onboarding/message   │ │
        │  │  • /api/clients              │ │
        │  │  • /api/webhooks             │ │
        │  └────────────┬─────────────────┘ │
        │               │                   │
        │  ┌────────────▼─────────────────┐ │
        │  │  LangGraph Workflow          │ │
        │  │  • Conversation State        │ │
        │  │  • Question Flow             │ │
        │  │  • Response Validation       │ │
        │  │  • Data Collection           │ │
        │  └────────────┬─────────────────┘ │
        │               │                   │
        │  ┌────────────▼─────────────────┐ │
        │  │  OpenAI GPT-4o               │ │
        │  │  • Natural Language          │ │
        │  │  • Structured Outputs        │ │
        │  │  • Context Management        │ │
        │  └──────────────────────────────┘ │
        └────────────┬───────────────────────┘
                     │
                     │  Supabase Client
                     │
                     ▼
        ┌────────────────────────────────────┐
        │   SUPABASE (PostgreSQL + RLS)     │
        │                                    │
        │  ┌──────────────────────────────┐ │
        │  │  Tables                      │ │
        │  │  • tenants                   │ │
        │  │  • clients                   │ │
        │  └──────────────────────────────┘ │
        │                                    │
        │  ┌──────────────────────────────┐ │
        │  │  Row-Level Security (RLS)    │ │
        │  │  • Tenant Isolation          │ │
        │  │  • Policy Enforcement        │ │
        │  └──────────────────────────────┘ │
        │                                    │
        │  ┌──────────────────────────────┐ │
        │  │  Features                    │ │
        │  │  • Auto Backups              │ │
        │  │  • Connection Pooling        │ │
        │  │  • Real-time Subscriptions   │ │
        │  └──────────────────────────────┘ │
        └────────────┬───────────────────────┘
                     │
                     │  Webhook Trigger
                     │  (on completion)
                     │
                     ▼
        ┌────────────────────────────────────┐
        │         n8n AUTOMATION             │
        │                                    │
        │  ┌──────────────────────────────┐ │
        │  │  Workflow Steps              │ │
        │  │  1. Receive Webhook          │ │
        │  │  2. Fetch Client Data        │ │
        │  │  3. Map Fields               │ │
        │  │  4. Create GHL Contact       │ │
        │  │  5. Trigger GHL Workflow     │ │
        │  │  6. Update Backend           │ │
        │  └──────────────────────────────┘ │
        │                                    │
        │  ┌──────────────────────────────┐ │
        │  │  Error Handling              │ │
        │  │  • Retry Logic               │ │
        │  │  • Exponential Backoff       │ │
        │  │  • Failure Logging           │ │
        │  └──────────────────────────────┘ │
        └────────────┬───────────────────────┘
                     │
                     │  GoHighLevel API
                     │
                     ▼
        ┌────────────────────────────────────┐
        │         GOHIGHLEVEL                │
        │                                    │
        │  • Contact Created                 │
        │  • Custom Fields Populated         │
        │  • Workflow Triggered              │
        │  • Team Notified                   │
        └────────────────────────────────────┘
```

---

## Data Flow Sequence

### Onboarding Flow

```
1. User → Backend: POST /onboarding/start
   ↓
2. Backend → Database: Create client record
   ↓
3. Backend → LangGraph: Initialize conversation
   ↓
4. Backend → User: Return session_id + first question
   ↓
5. User → Backend: POST /onboarding/message (with answer)
   ↓
6. Backend → LangGraph: Process message
   ↓
7. LangGraph → Validators: Validate response
   ↓
8. LangGraph → OpenAI: Get next question (if needed)
   ↓
9. LangGraph → Database: Save progress
   ↓
10. Backend → User: Return next question
   ↓
   (Repeat steps 5-10 for each question)
   ↓
11. LangGraph: Mark as complete
   ↓
12. Backend → n8n: Trigger webhook
   ↓
13. n8n → GoHighLevel: Create contact
   ↓
14. n8n → Backend: Update with GHL contact ID
   ↓
15. Backend → Database: Store GHL contact ID
```

### Dashboard Flow

```
1. User → Dashboard: Visit /dashboard
   ↓
2. Dashboard → Supabase: Query clients (with RLS)
   ↓
3. Supabase → Dashboard: Return filtered clients
   ↓
4. Dashboard → User: Display table
   ↓
5. User: Click client
   ↓
6. Dashboard → Supabase: Query client details
   ↓
7. Supabase → Dashboard: Return full client data
   ↓
8. Dashboard → User: Show detail page
```

---

## Component Architecture

### Backend Structure

```
FastAPI Application
├── API Layer (Routers)
│   ├── Onboarding Endpoints
│   ├── Client Endpoints
│   └── Webhook Endpoints
│
├── Service Layer
│   ├── LangGraph Workflow
│   ├── Conversation State
│   └── Validators
│
├── Data Layer
│   ├── Pydantic Models
│   └── Supabase Client
│
└── Core
    ├── Configuration
    └── Middleware
```

### Frontend Structure

```
Next.js App
├── App Router (Pages)
│   ├── Dashboard Layout
│   ├── Client List Page
│   └── Client Detail Page
│
├── Components
│   ├── UI Components (shadcn)
│   ├── ClientsTable
│   ├── ClientCard
│   ├── SearchBar
│   └── ConversationHistory
│
├── Library (Utils)
│   ├── API Client
│   ├── Supabase Client
│   └── Helper Functions
│
└── Providers
    └── React Query
```

---

## Security Layers

```
┌─────────────────────────────────────┐
│  HTTPS / TLS Encryption             │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  CORS Restrictions                  │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Input Validation (Pydantic)        │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Row-Level Security (RLS)           │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Encrypted Environment Variables    │
└─────────────────────────────────────┘
```

---

## Deployment Architecture

### Development

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │    │   Backend    │    │   n8n        │
│ localhost:3k │◄──►│ localhost:8k │◄──►│ localhost:5k │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  Supabase    │
                  │   (Cloud)    │
                  └──────────────┘
```

### Production

```
┌──────────────────┐
│   Vercel (CDN)   │ ◄── Frontend (Global Edge)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Railway/Render  │ ◄── Backend API (US/EU)
└────────┬─────────┘
         │
         ├──────► ┌──────────────┐
         │        │  Supabase    │ ◄── Database (Multi-region)
         │        └──────────────┘
         │
         └──────► ┌──────────────┐
                  │  n8n Cloud   │ ◄── Automation (Cloud)
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ GoHighLevel  │ ◄── CRM Integration
                  └──────────────┘
```

---

## Technology Stack Layers

```
┌────────────────────────────────────────┐
│  PRESENTATION LAYER                    │
│  • Next.js 15                          │
│  • React 18                            │
│  • Tailwind CSS                        │
│  • shadcn/ui                           │
└────────────┬───────────────────────────┘
             │
┌────────────▼───────────────────────────┐
│  API LAYER                             │
│  • FastAPI                             │
│  • REST Endpoints                      │
│  • OpenAPI/Swagger                     │
└────────────┬───────────────────────────┘
             │
┌────────────▼───────────────────────────┐
│  BUSINESS LOGIC LAYER                  │
│  • LangGraph Workflows                 │
│  • LangChain                           │
│  • OpenAI GPT-4o                       │
│  • Pydantic Validation                 │
└────────────┬───────────────────────────┘
             │
┌────────────▼───────────────────────────┐
│  DATA LAYER                            │
│  • Supabase (PostgreSQL)               │
│  • Row-Level Security                  │
│  • JSONB Storage                       │
└────────────┬───────────────────────────┘
             │
┌────────────▼───────────────────────────┐
│  INTEGRATION LAYER                     │
│  • n8n Workflows                       │
│  • GoHighLevel API                     │
│  • Webhooks                            │
└────────────────────────────────────────┘
```

---

## Request/Response Flow Example

### Onboarding Start Request

```
Client                 Backend              Database          LangGraph
  │                      │                     │                │
  ├─POST /start─────────►│                     │                │
  │                      ├─INSERT client──────►│                │
  │                      │                     ├─Return UUID────┤
  │                      ├─Init state─────────────────────────►│
  │                      │                     │                │
  │                      ◄─────────────────────────────────────┤
  │◄─session_id + msg────┤                     │                │
  │                      │                     │                │
```

### Message Exchange

```
Client                 Backend              LangGraph         Validators      OpenAI
  │                      │                     │                │              │
  ├─POST /message───────►│                     │                │              │
  │                      ├─Process msg────────►│                │              │
  │                      │                     ├─Validate──────►│              │
  │                      │                     │◄─Valid─────────┤              │
  │                      │                     ├─Get next Q───────────────────►│
  │                      │                     │◄─Question──────────────────────│
  │                      │                     ├─Save state───►DB              │
  │                      │◄─Return response────┤                │              │
  │◄─Next question────────┤                     │                │              │
  │                      │                     │                │              │
```

This architecture provides a clear visual understanding of how all components interact!
