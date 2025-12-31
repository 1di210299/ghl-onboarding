# GoHighLevel Integration Guide

## 🎯 Overview

This guide explains how to integrate the onboarding system with GoHighLevel (GHL) to automatically create contacts and sync all collected data.

## ✅ What Gets Synced

When a client completes the 48-question onboarding:

1. **Contact is created in GHL** with basic info
2. **48 custom fields** are populated with all answers
3. **Tags are applied** based on responses
4. **Optional workflow is triggered** for follow-up automation

---

## 🔑 Step 1: Get GHL API Credentials

### 1.1 Get API Key

1. Log in to GoHighLevel: https://app.gohighlevel.com
2. Go to **Settings** → **Integrations** → **API**
3. Click **Generate API Key** or copy existing key
4. Save this key (you'll need it for `.env`)

### 1.2 Get Location ID

**Option A: From Agency Dashboard**
1. Go to **Agency View**
2. Select a sub-account
3. Look at the URL: `https://app.gohighlevel.com/location/{LOCATION_ID}`
4. Copy the `LOCATION_ID` from the URL

**Option B: Using API**
```bash
curl -X GET "https://services.leadconnectorhq.com/locations/" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 1.3 Get Workflow ID (Optional)

If you want to trigger a workflow after onboarding:

1. Go to **Workflows** in GHL
2. Create or select a workflow
3. Look at the URL: `https://app.gohighlevel.com/workflows/{WORKFLOW_ID}`
4. Copy the `WORKFLOW_ID`

---

## 🛠️ Step 2: Configure Backend

### 2.1 Update .env File

Edit `/Users/1di/ghl-onboarding/backend/.env`:

```bash
# GoHighLevel Configuration
GHL_API_KEY=ey...your-actual-api-key-here
GHL_LOCATION_ID=abc123...your-location-id
GHL_WORKFLOW_ID=wf_xyz...optional-workflow-id
GHL_API_URL=https://services.leadconnectorhq.com
```

### 2.2 Restart Backend

```bash
cd backend
source .venv/bin/activate
python run.py
```

---

## 📋 Step 3: Create Custom Fields in GHL

The system maps 48 questions to custom fields. You need to create these in GHL:

### 3.1 Access Custom Fields

1. Go to **Settings** → **Custom Fields**
2. Click **Add Custom Field**

### 3.2 Required Custom Fields

Create these custom fields (or map to existing ones):

**Quick Start Fields:**
- `birthday` - Text
- `practice_legal_name` - Text
- `practice_ein` - Text
- `office_address` - Text Area
- `home_address` - Text Area
- `texting_line` - Phone

**Team & Tech Fields:**
- `team_members` - Text Area
- `point_person` - Text
- `communication_preference` - Dropdown (Email, Phone, Text, Slack, Teams)
- `current_ehr` - Text
- `has_marketing_team` - Boolean
- `marketing_budget` - Text
- `existing_crm` - Text

**Identity & Brand Fields:**
- `brand_personality` - Text Area
- `practice_culture` - Text Area
- `target_audience` - Text Area
- `patient_terminology` - Dropdown (Patients, Members, Clients)
- `specialties` - Text Area
- `unique_services` - Text Area
- `brand_colors` - Text
- `has_logo` - Boolean
- `tagline` - Text
- `brand_guidelines` - Text Area
- `elevator_pitch` - Text Area
- `success_stories` - Text Area

**Digital & Growth Fields:**
- `has_website` - Boolean
- `website_url` - URL
- `website_satisfaction` - Number (1-5)
- `online_booking` - Boolean
- `accepts_new_patients` - Boolean
- `social_platforms` - Multi-select
- `instagram_handle` - Text
- `facebook_page` - Text
- `social_posting_frequency` - Text
- `social_growth_goal` - Text Area
- `content_topics` - Text Area
- `content_formats` - Text Area
- `review_platforms` - Multi-select
- `average_rating` - Number (1-5)
- `review_response` - Boolean
- `growth_goals` - Text Area
- `patient_acquisition` - Text Area
- `automation_interest` - Text Area
- `monthly_budget` - Text
- `additional_notes` - Text Area

---

## 🧪 Step 4: Test the Integration

### 4.1 Complete an Onboarding

1. Go to: http://localhost:3000/onboarding
2. Fill in practice info
3. Use the ✨ Auto-fill button to speed through questions
4. Complete all 48 questions

### 4.2 Verify in GHL

1. Go to **Contacts** in GHL
2. Search for the email used
3. Verify:
   - ✅ Contact was created
   - ✅ Basic info (name, email, phone) is correct
   - ✅ Custom fields are populated
   - ✅ Tags are applied: "Onboarding Completed"

### 4.3 Check Backend Logs

```bash
# Watch the logs
tail -f backend/logs/app.log

# Look for:
"Onboarding completed for session..."
"Successfully synced to GHL. Contact ID: ..."
```

---

## 🏷️ Automatic Tags

The system applies these tags based on answers:

- `Onboarding Completed` - Always applied
- `Has Marketing Team` - If Q14 = Yes
- `Has Website` - If Q29 = Yes
- `Online Booking Enabled` - If Q32 = Yes

---

## 🔄 Workflow Triggers

If you set `GHL_WORKFLOW_ID`, the system will:

1. Create/update the contact
2. Populate all custom fields
3. Apply tags
4. **Trigger the specified workflow**

This allows you to:
- Send welcome emails
- Schedule follow-up calls
- Assign to team members
- Start nurture sequences

---

## 📊 Field Mapping Reference

| Question | Field Name | GHL Custom Field |
|----------|------------|------------------|
| Q1 | q1_admin | First/Last Name (split) |
| Q2 | q2_culture | birthday |
| Q3 | q3_legal | practice_legal_name |
| Q4 | q4_legal | practice_ein |
| Q5 | q5_admin | office_address |
| Q6 | q6_admin | home_address |
| Q7 | q7_suite_setup | Phone (standard field) |
| Q8 | q8_suite_setup | texting_line |
| Q9 | q9_admin | Email (standard field) |
| ... | ... | ... (see full mapping in code) |

---

## 🐛 Troubleshooting

### Error: "GHL API error: 401"
- **Cause**: Invalid API key
- **Fix**: Verify `GHL_API_KEY` in `.env`

### Error: "GHL API error: 404"
- **Cause**: Invalid location ID
- **Fix**: Verify `GHL_LOCATION_ID` is correct

### Contact created but fields empty
- **Cause**: Custom fields don't exist in GHL
- **Fix**: Create all custom fields as listed above

### Workflow not triggering
- **Cause**: Invalid workflow ID or workflow not published
- **Fix**: 
  1. Verify workflow ID
  2. Ensure workflow is **Published** in GHL
  3. Check workflow trigger type

### Sync taking too long
- **Solution**: Sync happens in background (async)
- Check logs after 5-10 seconds
- Contact will appear even if workflow fails

---

## 💡 Pro Tips

1. **Create a template sub-account** with all custom fields configured
2. **Use workflow** to route to appropriate team member based on answers
3. **Set up email notifications** when onboarding completes
4. **Review tags** to segment contacts for follow-up
5. **Export data** from GHL for reporting/analysis

---

## 📞 Support

If sync fails:
1. Check backend logs: `backend/logs/app.log`
2. Verify all environment variables
3. Test GHL API manually with curl
4. Check GHL API status: https://status.gohighlevel.com

---

## 🎯 Next Steps

After successful integration:
- [ ] Create follow-up workflow in GHL
- [ ] Set up email templates
- [ ] Configure team assignments
- [ ] Build reporting dashboard
- [ ] Train team on system

---

**Need help?** Check the main [README](../README.md) or [API docs](API.md).
