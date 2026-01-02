#!/usr/bin/env python3
"""Script to create all necessary custom fields in GHL for onboarding"""

import httpx
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# All custom fields needed for the onboarding system
CUSTOM_FIELDS = [
    # Quick Start (Q1-Q9)
    {"name": "Birthday", "dataType": "TEXT", "placeholder": "MM/DD/YYYY"},
    {"name": "Practice EIN", "dataType": "TEXT", "placeholder": "XX-XXXXXXX"},
    {"name": "Office Address", "dataType": "TEXT", "placeholder": "Full office address"},
    {"name": "Home Address", "dataType": "TEXT", "placeholder": "Full home address"},
    {"name": "Texting Line", "dataType": "TEXT", "placeholder": "Phone number for texts"},
    
    # Team & Tech (Q10-Q16)
    {"name": "Team Members", "dataType": "LARGE_TEXT", "placeholder": "List of team members"},
    {"name": "Point Person", "dataType": "TEXT", "placeholder": "Main contact person"},
    {"name": "Communication Preference", "dataType": "TEXT", "placeholder": "Preferred communication method"},
    {"name": "Current EHR", "dataType": "TEXT", "placeholder": "Current EHR system"},
    {"name": "Has Marketing Team", "dataType": "TEXT", "placeholder": "Yes/No"},
    {"name": "Marketing Budget", "dataType": "TEXT", "placeholder": "Monthly budget range"},
    {"name": "Existing CRM", "dataType": "TEXT", "placeholder": "Current CRM system"},
    
    # Identity & Brand (Q17-Q28)
    {"name": "Brand Personality", "dataType": "LARGE_TEXT", "placeholder": "How would you describe your brand?"},
    {"name": "Practice Culture", "dataType": "LARGE_TEXT", "placeholder": "Describe your practice culture"},
    {"name": "Target Audience", "dataType": "LARGE_TEXT", "placeholder": "Who are your ideal patients?"},
    {"name": "Patient Terminology", "dataType": "TEXT", "placeholder": "How do you refer to patients?"},
    {"name": "Specialties", "dataType": "LARGE_TEXT", "placeholder": "Main specialties offered"},
    {"name": "Unique Services", "dataType": "LARGE_TEXT", "placeholder": "What makes you unique?"},
    {"name": "Brand Colors", "dataType": "TEXT", "placeholder": "Primary brand colors"},
    {"name": "Has Logo", "dataType": "TEXT", "placeholder": "Yes/No"},
    {"name": "Tagline", "dataType": "TEXT", "placeholder": "Practice tagline or slogan"},
    {"name": "Brand Guidelines", "dataType": "TEXT", "placeholder": "Link to brand guidelines"},
    {"name": "Elevator Pitch", "dataType": "LARGE_TEXT", "placeholder": "30-second practice description"},
    {"name": "Success Stories", "dataType": "LARGE_TEXT", "placeholder": "Patient success stories"},
    
    # Digital & Growth (Q29-Q48)
    {"name": "Has Website", "dataType": "TEXT", "placeholder": "Yes/No"},
    {"name": "Website URL", "dataType": "TEXT", "placeholder": "Practice website URL"},
    {"name": "Website Satisfaction", "dataType": "TEXT", "placeholder": "1-10 rating"},
    {"name": "Online Booking", "dataType": "TEXT", "placeholder": "Yes/No"},
    {"name": "Accepts New Patients", "dataType": "TEXT", "placeholder": "Yes/No"},
    {"name": "Social Platforms", "dataType": "LARGE_TEXT", "placeholder": "Active social media platforms"},
    {"name": "Instagram Handle", "dataType": "TEXT", "placeholder": "@username"},
    {"name": "Facebook Page", "dataType": "TEXT", "placeholder": "Facebook page URL"},
    {"name": "Social Posting Frequency", "dataType": "TEXT", "placeholder": "How often do you post?"},
    {"name": "Social Growth Goal", "dataType": "LARGE_TEXT", "placeholder": "Social media goals"},
    {"name": "Content Topics", "dataType": "LARGE_TEXT", "placeholder": "Topics for content"},
    {"name": "Content Formats", "dataType": "LARGE_TEXT", "placeholder": "Preferred content formats"},
    {"name": "Review Platforms", "dataType": "LARGE_TEXT", "placeholder": "Where are your reviews?"},
    {"name": "Average Rating", "dataType": "TEXT", "placeholder": "Average star rating"},
    {"name": "Review Response", "dataType": "TEXT", "placeholder": "Yes/No - Do you respond?"},
    {"name": "Growth Goals", "dataType": "LARGE_TEXT", "placeholder": "Practice growth objectives"},
    {"name": "Patient Acquisition", "dataType": "LARGE_TEXT", "placeholder": "How do you get new patients?"},
    {"name": "Automation Interest", "dataType": "LARGE_TEXT", "placeholder": "What would you like to automate?"},
    {"name": "Monthly Budget", "dataType": "TEXT", "placeholder": "Marketing budget range"},
    {"name": "Additional Notes", "dataType": "LARGE_TEXT", "placeholder": "Any additional information"},
]

async def create_custom_fields():
    """Create all custom fields in GHL."""
    
    api_key = os.getenv('GHL_API_KEY')
    location_id = os.getenv('GHL_LOCATION_ID')
    
    if not api_key:
        print("❌ Error: GHL_API_KEY not set in backend/.env file")
        return
    
    url = "https://rest.gohighlevel.com/v1/custom-fields/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Creating custom fields in GHL...")
    print(f"   Location ID: {location_id}")
    print(f"   Total fields to create: {len(CUSTOM_FIELDS)}\n")
    
    created = 0
    skipped = 0
    failed = 0
    
    # First, get existing fields
    print("📋 Fetching existing fields...")
    existing_fields = {}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                existing_fields = {
                    field["name"].lower(): field["id"]
                    for field in data.get("customFields", [])
                }
                print(f"   Found {len(existing_fields)} existing fields\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch existing fields: {e}\n")
    
    print("=" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, field in enumerate(CUSTOM_FIELDS, 1):
                field_name = field["name"]
                
                # Check if field already exists
                if field_name.lower() in existing_fields:
                    print(f"[{i}/{len(CUSTOM_FIELDS)}] ⏭️  Skipped: {field_name} (already exists)")
                    skipped += 1
                    continue
                
                # Create the field
                try:
                    response = await client.post(
                        url,
                        headers=headers,
                        json=field
                    )
                    
                    if response.status_code in [200, 201]:
                        result = response.json()
                        field_id = result.get("customField", {}).get("id", "unknown")
                        print(f"[{i}/{len(CUSTOM_FIELDS)}] ✅ Created: {field_name} → {field_id}")
                        created += 1
                        
                        # Small delay to avoid rate limiting
                        await asyncio.sleep(0.5)
                    else:
                        print(f"[{i}/{len(CUSTOM_FIELDS)}] ❌ Failed: {field_name}")
                        print(f"   Status: {response.status_code}")
                        print(f"   Response: {response.text[:200]}")
                        failed += 1
                
                except Exception as e:
                    print(f"[{i}/{len(CUSTOM_FIELDS)}] ❌ Error creating {field_name}: {e}")
                    failed += 1
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✅ Created: {created}")
    print(f"⏭️  Skipped: {skipped} (already existed)")
    print(f"❌ Failed: {failed}")
    print(f"📝 Total: {len(CUSTOM_FIELDS)}")
    print("\n💡 Tip: Run python get_fields.py to see all fields with their IDs")

if __name__ == "__main__":
    asyncio.run(create_custom_fields())
