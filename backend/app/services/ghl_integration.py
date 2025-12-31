"""
GoHighLevel API Integration Service.
Handles syncing onboarding data to GHL contacts and custom fields.
"""

import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class GHLIntegrationService:
    """Service for integrating with GoHighLevel API."""
    
    def __init__(self, api_key: str, location_id: str):
        """
        Initialize GHL integration service.
        
        Args:
            api_key: GHL API key
            location_id: GHL location (sub-account) ID
        """
        self.api_key = api_key
        self.location_id = location_id
        self.base_url = "https://rest.gohighlevel.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_or_update_contact(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        source: str = "Onboarding System"
    ) -> Dict[str, Any]:
        """
        Create or update a contact in GHL.
        
        Args:
            email: Contact email (required)
            first_name: Contact first name
            last_name: Contact last name
            phone: Contact phone number
            custom_fields: Dictionary of custom field values
            tags: List of tags to apply
            source: Source of the contact
            
        Returns:
            GHL contact data with ID
        """
        try:
            # Prepare contact data
            contact_data = {
                "email": email,
                "source": source
            }
            
            if first_name:
                contact_data["firstName"] = first_name
            if last_name:
                contact_data["lastName"] = last_name
            if phone:
                contact_data["phone"] = phone
            if tags:
                contact_data["tags"] = tags
            if custom_fields:
                # Format: [{"id": "field_id", "value": "value"}]
                contact_data["customField"] = [
                    {"id": field_id, "value": value}
                    for field_id, value in custom_fields.items()
                ]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First, try to find existing contact by email
                search_response = await client.get(
                    f"{self.base_url}/contacts/",
                    headers=self.headers,
                    params={"email": email}
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    contacts = search_data.get("contacts", [])
                    
                    if contacts and len(contacts) > 0:
                        # Update existing contact
                        contact_id = contacts[0]["id"]
                        logger.info(f"Updating existing GHL contact: {contact_id}")
                        
                        update_response = await client.put(
                            f"{self.base_url}/contacts/{contact_id}",
                            headers=self.headers,
                            json=contact_data
                        )
                        
                        if update_response.status_code in [200, 201]:
                            result = update_response.json()
                            logger.info(f"Successfully updated GHL contact: {contact_id}")
                            return result.get("contact", result)
                        else:
                            logger.error(f"Failed to update GHL contact: {update_response.text}")
                            raise Exception(f"GHL API error: {update_response.status_code}")
                
                # Create new contact
                logger.info(f"Creating new GHL contact for: {email}")
                create_response = await client.post(
                    f"{self.base_url}/contacts/",
                    headers=self.headers,
                    json=contact_data
                )
                
                if create_response.status_code in [200, 201]:
                    result = create_response.json()
                    logger.info(f"Successfully created GHL contact: {result.get('contact', {}).get('id')}")
                    return result.get("contact", result)
                else:
                    logger.error(f"Failed to create GHL contact: {create_response.text}")
                    raise Exception(f"GHL API error: {create_response.status_code}")
        
        except httpx.TimeoutException:
            logger.error("GHL API request timed out")
            raise Exception("GHL API timeout")
        except Exception as e:
            logger.error(f"Error in GHL integration: {e}")
            raise
    
    async def add_tag_to_contact(self, contact_id: str, tag: str) -> bool:
        """
        Add a tag to a GHL contact.
        
        Args:
            contact_id: GHL contact ID
            tag: Tag name to add
            
        Returns:
            Success status
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/contacts/{contact_id}/tags",
                    headers=self.headers,
                    json={"tags": [tag]}
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Added tag '{tag}' to contact {contact_id}")
                    return True
                else:
                    logger.error(f"Failed to add tag: {response.text}")
                    return False
        
        except Exception as e:
            logger.error(f"Error adding tag to contact: {e}")
            return False
    
    async def trigger_workflow(self, contact_id: str, workflow_id: str) -> bool:
        """
        Trigger a GHL workflow for a contact.
        
        Args:
            contact_id: GHL contact ID
            workflow_id: GHL workflow ID to trigger
            
        Returns:
            Success status
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/workflows/{workflow_id}/subscribers",
                    headers=self.headers,
                    json={"contactId": contact_id}
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Triggered workflow {workflow_id} for contact {contact_id}")
                    return True
                else:
                    logger.error(f"Failed to trigger workflow: {response.text}")
                    return False
        
        except Exception as e:
            logger.error(f"Error triggering workflow: {e}")
            return False
    
    def map_onboarding_data_to_ghl(self, onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map onboarding questions to GHL contact fields.
        
        Args:
            onboarding_data: Dictionary with all onboarding answers
            
        Returns:
            Mapped data ready for GHL
        """
        # Extract name from Q1 (full name)
        full_name = onboarding_data.get('q1_admin', '').strip()
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Basic contact info
        contact_data = {
            "email": onboarding_data.get('q9_admin', ''),  # Q9: email
            "first_name": first_name,
            "last_name": last_name,
            "phone": onboarding_data.get('q7_suite_setup', ''),  # Q7: phone
        }
        
        # Custom fields mapping
        # NOTE: These keys should be the GHL custom field IDs (not names)
        # Run: curl with GHL API to get all custom field IDs, or check GHL dashboard
        # Format: {"custom_field_id": "value"}
        # 
        # Known field IDs:
        # - v3qz5dhJBIuNJWUi1LGW: Practice Legal Name
        # - LMVDJCOZLXnoy3jkozSv: Message (for notes)
        # - S73hTOb1vaQu5X6YxOPf: Age
        # 
        # TODO: Create remaining custom fields in GHL and update these IDs
        custom_fields = {
            # Quick Start (Q1-Q9) - UPDATE THESE IDs WITH YOUR GHL CUSTOM FIELD IDs
            "v3qz5dhJBIuNJWUi1LGW": onboarding_data.get('q3_legal'),  # Practice Legal Name
            "LMVDJCOZLXnoy3jkozSv": onboarding_data.get('q48_notes'),  # Additional notes/message
            # TODO: Create these fields in GHL Settings -> Custom Fields:
            # - Practice EIN (TEXT): onboarding_data.get('q4_legal')
            # - Office Address (TEXT_AREA): onboarding_data.get('q5_admin')
            # - Home Address (TEXT_AREA): onboarding_data.get('q6_admin')
            # - Birthday (TEXT): onboarding_data.get('q2_culture')
            # - Phone/Texting Line (TEXT): onboarding_data.get('q8_suite_setup')
            # - Team Members (TEXT_AREA): onboarding_data.get('q10_team')
            # - Point Person (TEXT): onboarding_data.get('q11_client_lead')
            # - Communication Preference (SINGLE_OPTIONS): onboarding_data.get('q12_admin')
            # - Current EHR (TEXT): onboarding_data.get('q13_tech')
            # - Has Marketing Team (SINGLE_OPTIONS): onboarding_data.get('q14_marketing')
            # - Marketing Budget (TEXT): onboarding_data.get('q15_marketing')
            # - Brand Personality (TEXT_AREA): onboarding_data.get('q17_personality')
            # - Target Audience (TEXT_AREA): onboarding_data.get('q19_personality')
            # - Specialties (TEXT_AREA): onboarding_data.get('q21_services')
            # - Brand Colors (TEXT): onboarding_data.get('q23_brand')
            # - Tagline (TEXT): onboarding_data.get('q25_brand')
            # - Elevator Pitch (TEXT_AREA): onboarding_data.get('q27_messaging')
            # - Website URL (TEXT): onboarding_data.get('q30_online')
            # - Instagram Handle (TEXT): onboarding_data.get('q35_social')
            # - Facebook Page (TEXT): onboarding_data.get('q36_social')
            # - Growth Goals (TEXT_AREA): onboarding_data.get('q44_growth')
            # - Monthly Budget (TEXT): onboarding_data.get('q47_budget')
            # ... (Add more as needed - see docs/guides/GHL_INTEGRATION.md for full list)
        }
            # ... (Add more as needed - see docs/guides/GHL_INTEGRATION.md for full list)
        }
        
        # Remove None values
        custom_fields = {k: v for k, v in custom_fields.items() if v is not None}
        
        # Tags based on responses
        tags = ["Onboarding Completed"]
        
        # Add tags based on specific answers
        if onboarding_data.get('q14_marketing') == 'Yes':
            tags.append("Has Marketing Team")
        if onboarding_data.get('q29_online') == 'Yes':
            tags.append("Has Website")
        if onboarding_data.get('q32_online') == 'Yes':
            tags.append("Online Booking Enabled")
        
        return {
            "contact_data": contact_data,
            "custom_fields": custom_fields,
            "tags": tags
        }
    
    async def sync_onboarding_to_ghl(
        self,
        onboarding_data: Dict[str, Any],
        practice_name: str,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete sync of onboarding data to GHL.
        
        Args:
            onboarding_data: All onboarding question answers
            practice_name: Practice name
            workflow_id: Optional workflow to trigger after sync
            
        Returns:
            GHL contact data and sync status
        """
        try:
            # Map onboarding data to GHL format
            mapped_data = self.map_onboarding_data_to_ghl(onboarding_data)
            
            # Add practice name to custom fields
            mapped_data["custom_fields"]["practice_name"] = practice_name
            
            # Create or update contact
            contact = await self.create_or_update_contact(
                email=mapped_data["contact_data"]["email"],
                first_name=mapped_data["contact_data"]["first_name"],
                last_name=mapped_data["contact_data"]["last_name"],
                phone=mapped_data["contact_data"]["phone"],
                custom_fields=mapped_data["custom_fields"],
                tags=mapped_data["tags"],
                source="AI Onboarding System"
            )
            
            contact_id = contact.get("id")
            
            # Trigger workflow if provided
            if workflow_id and contact_id:
                await self.trigger_workflow(contact_id, workflow_id)
            
            logger.info(f"Successfully synced onboarding to GHL contact: {contact_id}")
            
            return {
                "success": True,
                "contact_id": contact_id,
                "contact": contact,
                "synced_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to sync onboarding to GHL: {e}")
            return {
                "success": False,
                "error": str(e),
                "synced_at": datetime.utcnow().isoformat()
            }
