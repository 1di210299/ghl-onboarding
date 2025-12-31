# System Architecture - 48 Question Onboarding

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
│                                                                      │
│  Chat Interface → "Dr. John Smith" → Backend API                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND WORKFLOW                                │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. LOAD QUESTIONS                                            │  │
│  │     questions.json → load_questions_config()                 │  │
│  │     Result: 48 questions in memory                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                ↓                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  2. ASK QUESTION NODE                                         │  │
│  │     • Get question by index (e.g., index 0 = Q1)             │  │
│  │     • Check dependencies (skip if not met)                   │  │
│  │     • Update current_stage                                   │  │
│  │     • Format question text with options/notes                │  │
│  │     • Send to user                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                ↓                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  3. RECEIVE USER RESPONSE                                     │  │
│  │     "Dr. John Smith"                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                ↓                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  4. VALIDATE RESPONSE NODE                                    │  │
│  │     • Get validator type from question config                │  │
│  │     • Route to appropriate validator function                │  │
│  │       - text → validate_text()                               │  │
│  │       - email → validate_email()                             │  │
│  │       - boolean → validate_boolean()                         │  │
│  │       - choice → validate_choice(options)                    │  │
│  │       - multi_select → validate_multi_select(options)        │  │
│  │       - scale → validate_scale(1, 5)                         │  │
│  │     • Store in state using field_name (e.g., q1_admin)       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                ↓                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  5. SAVE DATA NODE                                            │  │
│  │     • Organize answers by stage                              │  │
│  │     • Save to appropriate JSONB column:                      │  │
│  │       - Q1-Q9   → quick_start_data                           │  │
│  │       - Q10-Q16 → team_tech_data                             │  │
│  │       - Q17-Q28 → identity_brand_data                        │  │
│  │       - Q29-Q48 → digital_growth_data                        │  │
│  │     • Update current_question and current_stage              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                ↓                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  6. DECISION NODE                                             │  │
│  │     • If step < 48: Go to step 2 (next question)             │  │
│  │     • If step == 48: Go to COMPLETE NODE                     │  │
│  │     • If validation failed: CLARIFY NODE                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATABASE (SUPABASE)                         │
│                                                                      │
│  clients table:                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ id (UUID)                                                    │   │
│  │ email                                                        │   │
│  │ current_stage: "Quick Start"                                │   │
│  │ current_question: 1                                         │   │
│  │                                                             │   │
│  │ quick_start_data (JSONB):                                  │   │
│  │   {                                                         │   │
│  │     "q1_admin": "Dr. John Smith",                          │   │
│  │     "q2_culture": "June 15",                               │   │
│  │     ...                                                     │   │
│  │   }                                                         │   │
│  │                                                             │   │
│  │ team_tech_data (JSONB): {...}                              │   │
│  │ identity_brand_data (JSONB): {...}                         │   │
│  │ digital_growth_data (JSONB): {...}                         │   │
│  │                                                             │   │
│  │ onboarding_completed: false                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  conversation_sessions table (for pause/resume):                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ id (UUID)                                                    │   │
│  │ client_id (FK)                                              │   │
│  │ session_id                                                  │   │
│  │ state_data (JSONB)                                          │   │
│  │ created_at                                                  │   │
│  │ updated_at                                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

See full architecture details in the project documentation.
