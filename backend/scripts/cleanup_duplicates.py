"""
Cleanup duplicate client records.
Keeps the most recent completed record, deletes incomplete duplicates.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import supabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_duplicates():
    """Remove duplicate client records, keeping the completed one."""
    
    try:
        # Get all clients for the tenant
        clients = supabase.service.table("clients").select(
            "*"
        ).eq(
            "tenant_id", "00000000-0000-0000-0000-000000000001"
        ).order("created_at", desc=True).execute()
        
        if not clients.data:
            logger.info("No clients found")
            return
        
        logger.info(f"Found {len(clients.data)} total clients")
        
        # Group by practice_name
        by_practice = {}
        for client in clients.data:
            name = client["practice_name"]
            if name not in by_practice:
                by_practice[name] = []
            by_practice[name].append(client)
        
        # Find duplicates
        for practice_name, records in by_practice.items():
            if len(records) > 1:
                logger.info(f"\nFound {len(records)} records for '{practice_name}':")
                
                # Sort by: completed first, then by created_at desc
                records.sort(key=lambda x: (
                    not x["onboarding_completed"],  # False (completed) comes first
                    -1 if x["created_at"] else 0  # Most recent
                ), reverse=False)
                
                # Keep the first (best) one
                keep = records[0]
                to_delete = records[1:]
                
                logger.info(f"  KEEP: {keep['id']} (completed={keep['onboarding_completed']}, created={keep['created_at']})")
                
                for record in to_delete:
                    logger.info(f"  DELETE: {record['id']} (completed={record['onboarding_completed']}, created={record['created_at']})")
                    
                    # Delete the duplicate
                    result = supabase.service.table("clients").delete().eq("id", record["id"]).execute()
                    logger.info(f"    ✓ Deleted")
        
        logger.info("\n✓ Cleanup complete!")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise


if __name__ == "__main__":
    cleanup_duplicates()
