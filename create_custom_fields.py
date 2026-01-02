"""
Script to create all custom fields in a GHL location using Agency API Key.
This script creates the 44 custom fields needed for the onboarding system.
"""

import httpx
import asyncio
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')

AGENCY_API_KEY = os.getenv('GHL_API_KEY')
LOCATION_ID = os.getenv('GHL_LOCATION_ID')
BASE_URL = "https://rest.gohighlevel.com/v1"

HEADERS = {
    "Authorization": f"Bearer {AGENCY_API_KEY}",
    "Version": "2021-07-28",
    "locationId": LOCATION_ID,
    "Content-Type": "application/json"
}

# Custom fields configuration from questions.json
CUSTOM_FIELDS = [
    {"name": "Practice Name", "dataType": "TEXT", "model": "contact"},
    {"name": "Doctor's First Name", "dataType": "TEXT", "model": "contact"},
    {"name": "Doctor's Last Name", "dataType": "TEXT", "model": "contact"},
    {"name": "Preferred Name", "dataType": "TEXT", "model": "contact"},
    {"name": "Birthday", "dataType": "TEXT", "model": "contact"},
    {"name": "Practice Legal Name", "dataType": "TEXT", "model": "contact"},
    {"name": "Practice EIN", "dataType": "TEXT", "model": "contact"},
    {"name": "Home Address", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Texting Line", "dataType": "TEXT", "model": "contact"},
    {"name": "Team Members", "dataType": "NUMERICAL", "model": "contact"},
    {"name": "Point Person", "dataType": "TEXT", "model": "contact"},
    {"name": "Has Marketing Team", "dataType": "TEXT", "model": "contact"},
    {"name": "Marketing Budget", "dataType": "TEXT", "model": "contact"},
    {"name": "Has Logo", "dataType": "TEXT", "model": "contact"},
    {"name": "Tagline", "dataType": "TEXT", "model": "contact"},
    {"name": "Brand Guidelines", "dataType": "TEXT", "model": "contact"},
    {"name": "Social Platforms", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Practice Type", "dataType": "TEXT", "model": "contact"},
    {"name": "Years in Practice", "dataType": "TEXT", "model": "contact"},
    {"name": "Patient Volume", "dataType": "TEXT", "model": "contact"},
    {"name": "Target Patients", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Has Website", "dataType": "TEXT", "model": "contact"},
    {"name": "Website URL", "dataType": "TEXT", "model": "contact"},
    {"name": "Website Description", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Special Certifications", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Unique Treatments", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Has Online Booking", "dataType": "TEXT", "model": "contact"},
    {"name": "Online Booking URL", "dataType": "TEXT", "model": "contact"},
    {"name": "Has Reviews", "dataType": "TEXT", "model": "contact"},
    {"name": "Reviews Summary", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Has Patient Financing", "dataType": "TEXT", "model": "contact"},
    {"name": "Financing Options", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Social Media Focus", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Content Types", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Posting Frequency", "dataType": "TEXT", "model": "contact"},
    {"name": "Has Email Marketing", "dataType": "TEXT", "model": "contact"},
    {"name": "Email Platform", "dataType": "TEXT", "model": "contact"},
    {"name": "Email Frequency", "dataType": "TEXT", "model": "contact"},
    {"name": "Has Paid Ads", "dataType": "TEXT", "model": "contact"},
    {"name": "Ad Platforms", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Monthly Ad Budget", "dataType": "TEXT", "model": "contact"},
    {"name": "Primary Goals", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Success Metrics", "dataType": "LARGE_TEXT", "model": "contact"},
    {"name": "Additional Notes", "dataType": "LARGE_TEXT", "model": "contact"},
]


async def create_custom_field(client: httpx.AsyncClient, field: dict) -> dict:
    """Create a single custom field in GHL."""
    url = f"{BASE_URL}/custom-fields/"
    
    payload = {
        "name": field["name"],
        "dataType": field["dataType"],
        "model": field["model"],
        "position": 0
    }
    
    try:
        response = await client.post(url, json=payload, headers=HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Created: {field['name']}")
            return {"success": True, "field": field["name"], "data": data}
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print(f"⚠️  Already exists: {field['name']}")
            return {"success": True, "field": field["name"], "message": "Already exists"}
        else:
            print(f"❌ Failed: {field['name']} - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return {"success": False, "field": field["name"], "error": response.text}
    
    except Exception as e:
        print(f"❌ Error creating {field['name']}: {str(e)}")
        return {"success": False, "field": field["name"], "error": str(e)}


async def main():
    """Create all custom fields."""
    print(f"🚀 Starting custom field creation...")
    print(f"📍 Location ID: {LOCATION_ID}")
    print(f"🔑 API Key length: {len(AGENCY_API_KEY)}")
    print(f"📊 Total fields to create: {len(CUSTOM_FIELDS)}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test API connection first
        print("🔍 Testing API connection...")
        test_url = f"{BASE_URL}/custom-fields/"
        try:
            test_response = await client.get(test_url, headers=HEADERS)
            if test_response.status_code == 200:
                existing_fields = test_response.json().get('customFields', [])
                print(f"✅ API connection successful! Found {len(existing_fields)} existing fields\n")
            else:
                print(f"❌ API test failed: {test_response.status_code}")
                print(f"Response: {test_response.text}\n")
                return
        except Exception as e:
            print(f"❌ Connection error: {str(e)}\n")
            return
        
        # Create all fields
        print("📝 Creating custom fields...\n")
        results = []
        for field in CUSTOM_FIELDS:
            result = await create_custom_field(client, field)
            results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        if failed:
            print("\n❌ Failed fields:")
            for f in failed:
                print(f"   - {f['field']}: {f.get('error', 'Unknown error')}")
        
        print("\n✅ Custom fields setup complete!")


if __name__ == "__main__":
    asyncio.run(main())
