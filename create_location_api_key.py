"""
Script to create a Location API Key for a specific GHL location.
This uses an existing Agency API Key to create a location-specific key.
"""

import httpx
import asyncio
from dotenv import load_dotenv
import os

# Load environment from backend/.env
load_dotenv('backend/.env')

AGENCY_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6Imh1U1pNWUF6dzlsaWNpNjZUMkVqIiwidmVyc2lvbiI6MSwiaWF0IjoxNzMyODYxNjQ3Mjg4LCJzdWIiOiJQckZ1VHJlUTN4UElEbzMwbkZLQyJ9.wdHtvE5BWrJ7KIfO06pskE9ezhWzWFYOQ2As-5nL6Hk"
NEW_LOCATION_ID = "taYzAjYbnrXSS0NqMPBW"

async def create_location_api_key():
    """Create a new Location API Key for the specified location."""
    
    url = f"https://rest.gohighlevel.com/v1/locations/{NEW_LOCATION_ID}/apiKey"
    
    headers = {
        "Authorization": f"Bearer {AGENCY_API_KEY}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }
    
    data = {
        "name": "Onboarding System - Auto Generated",
        "scopes": [
            "contacts.readonly",
            "contacts.write",
            "locations.readonly",
            "locations/customFields.readonly",
            "locations/customFields.write",
            "locations/tags.readonly",
            "locations/tags.write"
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"🔄 Creating Location API Key for location: {NEW_LOCATION_ID}")
            print(f"   Using endpoint: {url}")
            
            response = await client.post(url, headers=headers, json=data)
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"\n✅ SUCCESS! Location API Key created:")
                print(f"\nAPI Key: {result.get('apiKey', 'N/A')}")
                print(f"\n💡 Copy this key and update it in backend/.env:")
                print(f"   GHL_API_KEY={result.get('apiKey', 'N/A')}")
            else:
                print(f"\n❌ ERROR: {response.text}")
                print(f"\nℹ️  This might mean:")
                print(f"   1. The current API key doesn't have permission to create Location keys")
                print(f"   2. You need to use an Agency API Key (not a Location key)")
                print(f"   3. The location ID is incorrect")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_location_api_key())
