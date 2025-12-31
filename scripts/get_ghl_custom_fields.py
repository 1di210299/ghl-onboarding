#!/usr/bin/env python3
"""
Script to fetch all custom fields from GoHighLevel and generate ID mappings.
Run this to get the correct custom field IDs for your GHL location.

Usage:
    python scripts/get_ghl_custom_fields.py
"""

import httpx
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings


async def fetch_custom_fields():
    """Fetch all custom fields from GHL."""
    
    if not settings.ghl_api_key:
        print("❌ Error: GHL_API_KEY not set in .env file")
        return
    
    url = f"{settings.ghl_api_url}/custom-fields/"
    headers = {
        "Authorization": f"Bearer {settings.ghl_api_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Fetching custom fields from GoHighLevel...")
    print(f"   API URL: {url}\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
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
                print("PYTHON MAPPING (for ghl_integration.py)")
                print("=" * 80)
                print("\ncustom_fields = {")
                
                # Suggest mappings for common onboarding fields
                field_map = {
                    "practice legal name": "practice_legal_name",
                    "practice_ein": "practice_ein",
                    "office_address": "office_address",
                    "home_address": "home_address",
                    "birthday": "birthday",
                    "message": "additional_notes",
                    "age": "age"
                }
                
                for field in custom_fields:
                    name_lower = field.get("name", "").lower()
                    field_id = field.get("id", "")
                    
                    # Try to match with known fields
                    for pattern, var_name in field_map.items():
                        if pattern in name_lower:
                            print(f'    "{field_id}": onboarding_data.get("{var_name}"),  # {field["name"]}')
                            break
                
                print("}\n")
                
                print("\n💡 TIP: Copy the field IDs you need and update")
                print("   backend/app/services/ghl_integration.py -> map_onboarding_data_to_ghl()")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(fetch_custom_fields())
