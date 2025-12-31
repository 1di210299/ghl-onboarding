"""
Test configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def sample_client_data():
    """Sample client data for testing."""
    return {
        "practice_name": "Test Practice",
        "legal_name": "Test Practice LLC",
        "email": "test@practice.com",
        "phone": "(555) 123-4567",
        "address": {
            "street": "123 Main St",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90210"
        },
        "terminology_preference": "patients",
        "brand_colors": {
            "primary": "#FF5733",
            "secondary": "#0066CC"
        },
        "business_goals": [
            "Increase patient retention",
            "Launch telemedicine",
            "Improve online reputation"
        ]
    }
