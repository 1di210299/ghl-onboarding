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
    
    # Cache for custom field mappings (name -> id)
    _custom_fields_cache: Optional[Dict[str, str]] = None
    
    def __init__(self, api_key: str, location_id: str):
        """
        Initialize GHL integration service.
        
        Args:
            api_key: GHL API key (can be Agency or Location API key)
            location_id: GHL location (sub-account) ID
        """
        self.api_key = api_key
        self.location_id = location_id
        self.base_url = "https://rest.gohighlevel.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }
        
        # If using Agency API key, add location header
        # Agency keys typically start with 'eyJh' and are longer
        # Location keys embed the location_id in the JWT
        if location_id and len(api_key) > 200:
            # This is likely an Agency API key, add location header
            self.headers["locationId"] = location_id
    
    async def get_custom_fields_mapping(self) -> Dict[str, str]:
        """
        Get mapping of custom field names to their IDs.
        Caches the result to avoid repeated API calls.
        
        Returns:
            Dictionary mapping field name (lowercase) to field ID
        """
        if self._custom_fields_cache is not None:
            return self._custom_fields_cache
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/custom-fields/",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    fields = data.get("customFields", [])
                    
                    # Create mapping: lowercase name -> field ID
                    self._custom_fields_cache = {
                        field["name"].lower(): field["id"]
                        for field in fields
                    }
                    
                    logger.info(f"Loaded {len(self._custom_fields_cache)} custom fields from GHL")
                    return self._custom_fields_cache
                else:
                    logger.error(f"Failed to fetch custom fields: {response.text}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching custom fields: {e}")
            return {}
    
    async def create_custom_field(self, name: str, data_type: str = "TEXT", placeholder: str = "") -> Optional[str]:
        """
        Create a new custom field in GHL.
        
        Args:
            name: Field name
            data_type: Field type (TEXT, LARGE_TEXT, NUMERICAL, SINGLE_OPTIONS, etc.)
            placeholder: Placeholder text
            
        Returns:
            Field ID if created successfully, None otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/custom-fields/",
                    headers=self.headers,
                    json={
                        "name": name,
                        "dataType": data_type,
                        "placeholder": placeholder
                    }
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    field_id = result.get("customField", {}).get("id")
                    logger.info(f"Created custom field '{name}' with ID: {field_id}")
                    
                    # Update cache
                    if self._custom_fields_cache is not None:
                        self._custom_fields_cache[name.lower()] = field_id
                    
                    return field_id
                else:
                    logger.error(f"Failed to create custom field '{name}': {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error creating custom field '{name}': {e}")
            return None
    
    async def get_or_create_custom_field(self, name: str, data_type: str = "TEXT") -> Optional[str]:
        """
        Get custom field ID by name, creating it if it doesn't exist.
        
        Args:
            name: Field name
            data_type: Field type if creation is needed
            
        Returns:
            Field ID
        """
        mapping = await self.get_custom_fields_mapping()
        field_id = mapping.get(name.lower())
        
        if field_id:
            return field_id
        
        # Field doesn't exist, create it
        logger.info(f"Custom field '{name}' not found, creating it...")
        return await self.create_custom_field(name, data_type)
    
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
    
    async def map_onboarding_data_to_ghl(self, onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map onboarding questions to GHL contact fields.
        Automatically resolves custom field IDs by name.
        
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
        
        # Get custom field mappings (name -> ID)
        field_mapping = await self.get_custom_fields_mapping()
        
        # Define all custom field mappings by name
        # These will be automatically resolved to IDs
        custom_fields_by_name = {
            # Quick Start (Q1-Q9)
            "Birthday": onboarding_data.get('q2_culture'),
            "Practice Legal Name": onboarding_data.get('q3_legal'),
            "Practice EIN": onboarding_data.get('q4_legal'),
            "Office Address": onboarding_data.get('q5_admin'),
            "Home Address": onboarding_data.get('q6_admin'),
            "Texting Line": onboarding_data.get('q8_suite_setup'),
            
            # Team & Tech (Q10-Q16)
            "Team Members": onboarding_data.get('q10_team'),
            "Point Person": onboarding_data.get('q11_client_lead'),
            "Communication Preference": onboarding_data.get('q12_admin'),
            "Current EHR": onboarding_data.get('q13_tech'),
            "Has Marketing Team": onboarding_data.get('q14_marketing'),
            "Marketing Budget": onboarding_data.get('q15_marketing'),
            "Existing CRM": onboarding_data.get('q16_tech'),
            
            # Identity & Brand (Q17-Q28)
            "Brand Personality": onboarding_data.get('q17_personality'),
            "Practice Culture": onboarding_data.get('q18_personality'),
            "Target Audience": onboarding_data.get('q19_personality'),
            "Patient Terminology": onboarding_data.get('q20_personality'),
            "Specialties": onboarding_data.get('q21_services'),
            "Unique Services": onboarding_data.get('q22_services'),
            "Brand Colors": onboarding_data.get('q23_brand'),
            "Has Logo": onboarding_data.get('q24_brand'),
            "Tagline": onboarding_data.get('q25_brand'),
            "Brand Guidelines": onboarding_data.get('q26_brand'),
            "Elevator Pitch": onboarding_data.get('q27_messaging'),
            "Success Stories": onboarding_data.get('q28_messaging'),
            
            # Digital & Growth (Q29-Q48)
            "Has Website": onboarding_data.get('q29_online'),
            "Website URL": onboarding_data.get('q30_online'),
            "Website Satisfaction": onboarding_data.get('q31_online'),
            "Online Booking": onboarding_data.get('q32_online'),
            "Accepts New Patients": onboarding_data.get('q33_online'),
            "Social Platforms": onboarding_data.get('q34_social'),
            "Instagram Handle": onboarding_data.get('q35_social'),
            "Facebook Page": onboarding_data.get('q36_social'),
            "Social Posting Frequency": onboarding_data.get('q37_social'),
            "Social Growth Goal": onboarding_data.get('q38_social'),
            "Content Topics": onboarding_data.get('q39_content'),
            "Content Formats": onboarding_data.get('q40_content'),
            "Review Platforms": onboarding_data.get('q41_reputation'),
            "Average Rating": onboarding_data.get('q42_reputation'),
            "Review Response": onboarding_data.get('q43_reputation'),
            "Growth Goals": onboarding_data.get('q44_growth'),
            "Patient Acquisition": onboarding_data.get('q45_growth'),
            "Automation Interest": onboarding_data.get('q46_automation'),
            "Monthly Budget": onboarding_data.get('q47_budget'),
            "Additional Notes": onboarding_data.get('q48_notes'),
        }
        
        # Resolve field names to IDs
        custom_fields = {}
        for field_name, value in custom_fields_by_name.items():
            if value is None or value == '':
                continue
                
            field_id = field_mapping.get(field_name.lower())
            
            if field_id:
                custom_fields[field_id] = value
            else:
                logger.warning(f"Custom field '{field_name}' not found in GHL. Skipping...")
        
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
            mapped_data = await self.map_onboarding_data_to_ghl(onboarding_data)
            
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
