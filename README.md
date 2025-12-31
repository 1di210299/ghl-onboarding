# GHL Client Onboarding System

AI-powered conversational onboarding system for healthcare practices using GoHighLevel (GHL).

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account
- OpenAI API key

### Installation

1. **Clone and setup:**
```bash
# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

2. **Configure environment variables:**
```bash
# Backend (.env)
cp backend/.env.example backend/.env
# Add your API keys

# Frontend (.env.local)
cp frontend/.env.example frontend/.env.local
# Add your API URLs
```

3. **Setup database:**
```bash
# Run migrations in Supabase SQL Editor
cat database/migrations/*.sql
```

4. **Start services:**
```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
python run.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

5. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
ghl-onboarding/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration & database
│   │   ├── models/      # Pydantic models
│   │   ├── services/    # Business logic & LangGraph workflow
│   │   └── config/      # Questions configuration
│   └── run.py
├── frontend/            # Next.js frontend
│   ├── app/            # App routes
│   ├── components/     # React components
│   └── public/
├── database/           # Supabase migrations
│   └── migrations/
├── config/             # Source data files
│   ├── questions_parsed.json
│   └── Questions for onboarding.xlsx
├── scripts/            # Setup & utility scripts
├── tests/              # Test files
├── docs/               # Documentation
│   ├── API.md
│   ├── architecture/   # Architecture docs
│   ├── guides/         # User guides
│   └── status-reports/ # Project status
├── n8n/                # N8N workflows (optional)
└── docker-compose.yml  # Docker setup
```

## 🔑 Key Features

- **48 AI-Powered Questions** organized in 4 stages
- **Conversational Interface** using LangGraph state machine
- **Real-time Validation** with smart error handling
- **Multi-tenant Support** with PostgreSQL + RLS
- **Auto-fill Testing** with OpenAI-generated responses
- **Progress Tracking** with visual indicators
- **Data Persistence** in Supabase

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Architecture Overview](docs/architecture/ARCHITECTURE.md)
- [Quick Start Guide](docs/guides/QUICKSTART.md)
- [Deployment Guide](docs/guides/DEPLOYMENT.md)

## 🛠️ Technology Stack

**Backend:**
- FastAPI 0.109.0
- LangChain + LangGraph 1.0.5
- OpenAI GPT-4o
- Python 3.11

**Frontend:**
- Next.js 16.1.1
- React 18.3.1
- TypeScript
- Tailwind CSS

**Database:**
- Supabase (PostgreSQL)
- Row Level Security (RLS)

## 🧪 Testing

```bash
# Run integration tests
python tests/test_integration.py

# Test with auto-fill (in frontend)
# Click the purple ✨ button to generate AI responses
```

## 📖 Usage

### Starting an Onboarding Session

1. Navigate to http://localhost:3000/onboarding
2. Fill in practice name and email
3. Click "Start Onboarding"
4. Answer questions or use ✨ Auto-fill button

### Auto-Fill for Testing

Click the purple **✨ Sparkles** button to automatically generate realistic answers using OpenAI.

## 🚢 Deployment

See [Deployment Guide](docs/guides/DEPLOYMENT.md) for production setup.

## 📊 Onboarding Stages

1. **Quick Start (Q1-Q9)** - Basic info, contact details
2. **Team & Tech (Q10-Q16)** - Team structure, existing systems
3. **Identity & Brand (Q17-Q28)** - Brand personality, messaging
4. **Digital & Growth (Q29-Q48)** - Online presence, marketing goals

## 🐛 Troubleshooting

### Supabase Connection Timeout
1. Go to Supabase Dashboard
2. Project Settings → General → Restart Project

### Port Already in Use
```bash
# Kill processes
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

---

**Built with ❤️ for GoHighLevel Healthcare Agencies**
