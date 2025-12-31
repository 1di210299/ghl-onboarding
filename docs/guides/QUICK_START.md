# 🚀 Quick Start Guide - 48 Question Onboarding System

## Overview

Your backend now supports a complete 48-question onboarding system that dynamically asks questions, validates responses, handles conditional logic, and saves data organized by stages.

---

## 🎯 What You Got

### ✅ Complete Backend Integration
- **48 Questions** loaded from JSON config
- **10 Conditional dependencies** (auto-skip logic)
- **7 Validator types** (text, email, boolean, choice, multi-select, scale, long_text)
- **4 Stages** (Quick Start, Team & Tech, Identity & Brand, Digital & Growth)
- **Database schema** ready with JSONB stage columns

### ✅ Files Ready
```
backend/
  app/
    config/
      questions.json              ← 48 questions config (21KB)
    services/
      workflow.py                 ← Refactored for 48 questions ✅
      state.py                    ← 48 field definitions ✅
      validators.py               ← 7 validators ready ✅
database/
  migrations/
    002_add_48_questions.sql     ← Schema migration ✅
```

---

## 🏁 Getting Started (3 Steps)

### Step 1: Run Database Migration (5 min)

You need to run the migration file to add the new columns to your Supabase database.

**Option A: Via Supabase Dashboard**
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy contents of `database/migrations/002_add_48_questions.sql`
4. Paste and run

**Option B: Via Command Line**
```bash
psql -h <your-supabase-host> \
     -U postgres \
     -d postgres \
     -f database/migrations/002_add_48_questions.sql
```

**What it adds:**
- 4 JSONB columns: `quick_start_data`, `team_tech_data`, `identity_brand_data`, `digital_growth_data`
- 2 tracking columns: `current_stage`, `current_question`
- 1 new table: `conversation_sessions` (for pause/resume)
- Helper function: `get_stage_progress()`

### Step 2: Install Backend Dependencies (2 min)

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- FastAPI, LangChain, LangGraph
- OpenAI SDK
- Supabase client
- Validators (email, phone)

### Step 3: Set Up Environment Variables

Create `backend/.env`:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# OpenAI
OPENAI_API_KEY=sk-your-key

# GoHighLevel (if applicable)
GHL_API_KEY=your-ghl-key
GHL_LOCATION_ID=your-location-id

# App Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 🧪 Testing the System

### Test 1: Verify JSON Loading

```bash
cd /Users/1di/ghl-onboarding
python test_questions_config.py
```

**Expected output:**
```
✅ Config loaded successfully
   Version: 1.0
   Total questions: 48
   Number of stages: 4
```

### Test 2: Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Test 3: Test Onboarding Endpoint

```bash
# Create a test client session
curl -X POST http://localhost:8000/api/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test-client-123",
    "tenant_id": "test-tenant-456"
  }'
```

**Expected response:**
```json
{
  "session_id": "session-xxx",
  "message": "Hello! I'm here to help get your practice set up...",
  "question": "What is your full name?"
}
```

### Test 4: Send First Answer

```bash
curl -X POST http://localhost:8000/api/onboarding/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-xxx",
    "message": "Dr. John Smith"
  }'
```

**Expected response:**
```json
{
  "session_id": "session-xxx",
  "message": "Great! What is your birthday?",
  "current_question": 2,
  "stage": "Quick Start",
  "progress": "2/48"
}
```

---

## 📋 Understanding the Question Flow

### Stage 1: Quick Start (9 Questions)
```
Q1: Full name
Q2: Birthday
Q3: Practice name (legal)
Q4: Practice name (DBA)
Q5: Street address
Q6: City
Q7: State
Q8: ZIP code
Q9: EIN/Tax ID
```

### Stage 2: Team & Tech (7 Questions)
```
Q10: Number of providers
Q11: Number of staff
Q12: Staff roles (multi-select)
Q13: EHR system
Q14: Has marketing company? (Yes/No)
  └─ Q15: Marketing company name (conditional on Q14=Yes)
Q16: Current tools (multi-select)
```

### Stage 3: Identity & Brand (12 Questions)
```
Q17-Q20: Practice personality questions
Q21-Q22: Services offered
Q23-Q26: Branding (colors, logo, personality)
Q27-Q28: Messaging preferences
```

### Stage 4: Digital & Growth (20 Questions)
```
Q29: Has website? (Yes/No)
  ├─ Q30: Website URL (if Q29≠No)
  ├─ Q31: Why no website? (if Q29=No)
  └─ Q33: Website issues (if Q29≠No)
Q32: Website satisfaction (1-5 scale)
Q34: Social media platforms (multi-select)
  ├─ Q35: Instagram handle (if Instagram selected)
  ├─ Q36: Facebook page (if Facebook selected)
  ├─ Q37: LinkedIn URL (if LinkedIn selected)
  └─ Q38: Blog URL (if Blog selected)
Q39: Content creation preference
  └─ Q40: Human content topics (if Q39≠AI-only)
Q41-Q43: Reputation/reviews
Q44-Q47: Growth goals, challenges, automation, budget
Q48: Additional notes
```

---

## 🔧 Customizing Questions

### Adding a New Question

1. **Edit `backend/app/config/questions.json`**:

```json
{
  "id": "Q49",
  "section": "Growth",
  "text": "How did you hear about us?",
  "type": "Multiple Choice",
  "field_name": "q49_referral",
  "options": "Google, Social Media, Referral, Other",
  "dependency": null,
  "validator": "choice",
  "required": true
}
```

2. **Update `backend/app/services/state.py`**:

```python
q49_referral: Optional[str]
```

3. **Update `TOTAL_QUESTIONS` in `workflow.py`**:

```python
TOTAL_QUESTIONS = 49  # Changed from 48
```

4. **Update migration** to handle new field in appropriate stage JSONB

That's it! No need to change validation logic or routing code.

### Modifying a Question

Just edit `questions.json` - changes take effect immediately on server restart.

```json
{
  "id": "Q1",
  "text": "What is the name of the practice owner?",  ← Changed
  ...
}
```

---

## 🔍 Debugging Tips

### Issue: Question not appearing
**Check:**
1. Is the dependency satisfied? Log the state before asking
2. Is the question index correct? Remember it's 0-based
3. Is the JSON valid? Run `python -m json.tool backend/app/config/questions.json`

### Issue: Validation failing
**Check:**
1. Does the validator exist in `validators.py`?
2. Is the validator name spelled correctly in JSON?
3. Are the options formatted correctly (comma-separated)?

### Issue: Data not saving
**Check:**
1. Database migration run successfully?
2. Field name matches between JSON and state.py?
3. Check logs for Supabase connection errors

### View Logs

```bash
# Check backend logs
tail -f backend/logs/app.log

# Or use the built-in logging
# Logs appear in console when running with --reload
```

---

## 📊 Monitoring Progress

### Check Stage Progress in Database

```sql
SELECT 
  id,
  email,
  current_stage,
  current_question,
  get_stage_progress(id) as stage_progress
FROM clients
WHERE onboarding_completed = false;
```

### Check Collected Data

```sql
-- Quick Start data
SELECT 
  quick_start_data->>'q1_admin' as full_name,
  quick_start_data->>'q4_admin' as practice_name
FROM clients
WHERE id = 'your-client-id';

-- Team & Tech data
SELECT team_tech_data
FROM clients
WHERE id = 'your-client-id';
```

---

## 🎨 Frontend Integration

When you build the chat UI, you'll interact with these endpoints:

### Start Onboarding
```javascript
POST /api/onboarding/start
{
  "client_id": "uuid",
  "tenant_id": "uuid"
}

Response: {
  "session_id": "...",
  "message": "Hello! I'm here...",
  "question": "What is your full name?",
  "options": null,
  "question_type": "Short Text"
}
```

### Send Message
```javascript
POST /api/onboarding/message
{
  "session_id": "...",
  "message": "Dr. John Smith"
}

Response: {
  "session_id": "...",
  "message": "Great! What is your birthday?",
  "current_question": 2,
  "total_questions": 48,
  "stage": "Quick Start",
  "progress": "2/48",
  "validation_error": null
}
```

### Get Progress
```javascript
GET /api/onboarding/progress/{session_id}

Response: {
  "current_question": 15,
  "total_questions": 48,
  "current_stage": "Team & Tech",
  "stage_progress": {
    "Quick Start": "9/9 (100%)",
    "Team & Tech": "6/7 (86%)",
    "Identity & Brand": "0/12 (0%)",
    "Digital & Growth": "0/20 (0%)"
  },
  "is_completed": false
}
```

---

## 🚀 Production Checklist

Before going live:

- [ ] Database migration run on production
- [ ] Environment variables set
- [ ] Error tracking enabled (Sentry, etc.)
- [ ] Rate limiting configured
- [ ] CORS configured for frontend domain
- [ ] Logging level set appropriately
- [ ] Health check endpoint working
- [ ] GoHighLevel integration tested
- [ ] Backup strategy in place
- [ ] Session timeout configured

---

## 📚 Additional Resources

- **Full Question List**: `QUESTIONS_SUMMARY.md`
- **Technical Details**: `BACKEND_INTEGRATION_COMPLETE.md`
- **Integration Summary**: `INTEGRATION_SUMMARY.md`
- **Database Migration**: `database/migrations/002_add_48_questions.sql`
- **Questions Config**: `backend/app/config/questions.json`
- **Test Script**: `test_questions_config.py`

---

## 🆘 Need Help?

### Common Questions

**Q: Can I change the order of questions?**  
A: Yes, just reorder them in `questions.json`. The system uses array index.

**Q: Can I skip questions entirely?**  
A: Yes, set `required: false` and handle null values in your business logic.

**Q: Can I have nested dependencies?**  
A: Yes, e.g., Q40 depends on Q39, which could depend on something else.

**Q: Can I use this for multiple tenants?**  
A: Yes, the system is tenant-aware via `tenant_id` in state.

---

## 🎉 You're Ready!

Your backend is fully integrated and ready to handle 48 questions with:
- ✅ Dynamic loading
- ✅ Conditional logic
- ✅ Multi-type validation
- ✅ Stage organization
- ✅ Progress tracking

**Next**: Run the database migration and start testing! 🚀
