# Frontend - GHL Healthcare Onboarding System

React/Next.js frontend for the AI-powered client onboarding chat interface.

## Features

- ✅ Real-time chat interface for 48-question onboarding
- ✅ Progress tracking with visual indicators
- ✅ Responsive design with Tailwind CSS
- ✅ TypeScript for type safety
- ✅ Integration with FastAPI backend

## Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

## Installation

```bash
cd frontend
npm install
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Usage

### Start Onboarding

Navigate to `/onboarding` to start a new onboarding session:

```
http://localhost:3000/onboarding
```

### Components

**OnboardingChat** - Main chat component
- Props:
  - `tenantId` (string, required)
  - `practiceName` (string, optional)
  - `email` (string, optional)
  - `onComplete` (function, optional) - Callback when onboarding completes

**Example:**

```tsx
import OnboardingChat from '@/components/onboarding-chat';

<OnboardingChat
  tenantId="00000000-0000-0000-0000-000000000001"
  practiceName="Healthy Life Medical"
  email="contact@healthylife.com"
  onComplete={(clientId, data) => {
    console.log('Completed!', clientId, data);
  }}
/>
```

## API Integration

The frontend connects to these backend endpoints:

- `POST /api/onboarding/start` - Initialize session
- `POST /api/onboarding/message` - Send user response
- `GET /api/onboarding/status/{session_id}` - Get progress

## Build for Production

```bash
npm run build
npm start
```

## Deployment

Deploy to Vercel:

```bash
vercel deploy
```

Set environment variables in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` - Your production backend URL

## Folder Structure

```
frontend/
├── app/
│   ├── onboarding/
│   │   └── page.tsx          # Onboarding page
│   ├── dashboard/             # Dashboard pages
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── onboarding-chat.tsx    # Main chat component
│   ├── ui/                    # UI components
│   └── ...
└── lib/
    └── ...
```

## Tech Stack

- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP**: Fetch API

## Troubleshooting

### CORS Error

Make sure backend CORS is configured for your frontend URL in `backend/app/core/config.py`:

```python
cors_origins: list[str] = ["http://localhost:3000"]
```

### Connection Refused

Ensure backend is running:

```bash
cd backend
source .venv/bin/activate
python run.py
```

### 404 Not Found

Check that API URL is correct in frontend code:

```typescript
const response = await fetch('http://localhost:8000/api/onboarding/start', ...);
```
