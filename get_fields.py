#!/usr/bin/env python3
"""Quick script to get GHL custom fields"""

import httpx
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

async def fetch_custom_fields():
    """Fetch all custom fields from GHL."""
    
    api_key = os.getenv('GHL_API_KEY')
    location_id = os.getenv('GHL_LOCATION_ID')
    
    if not api_key:
        print("❌ Error: GHL_API_KEY not set in backend/.env file")
        return
    
    url = f"https://rest.gohighlevel.com/v1/custom-fields/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Fetching custom fields from GoHighLevel...")
    print(f"   Location ID: {location_id}")
    print(f"   API URL: {url}\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            print(f"Status: {response.status_code}\n")
            
            if response.status_code == 200:
                data = response.json()
                custom_fields = data.get("customFields", [])
                
                print(f"✅ Found {len(custom_fields)} custom fields\n")
                print("=" * 80)
                print("CUSTOM FIELD MAPPINGS")
                print("=" * 80)
                print(f"{'Field Name':<40} {'Field ID':<30} {'Type':<10}")
                print("-" * 80)
                
                for field in custom_fields:
                    name = field.get("name", "")
                    field_id = field.get("id", "")
                    data_type = field.get("dataType", "")
                    print(f"{name:<40} {field_id:<30} {data_type:<10}")
                
                print("\n" + "=" * 80)
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(fetch_custom_fields())
