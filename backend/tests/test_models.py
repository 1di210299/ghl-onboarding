"""
Tests for client models and validation.
"""

import pytest
from app.models import Address, BrandColors, ClientData

def test_address_validation():
    """Test address validation."""
    # Valid address
    address = Address(
        street="123 Main St",
        city="Los Angeles",
        state="CA",
        zip="90210"
    )
    assert address.state == "CA"
    assert address.zip == "90210"
    
    # Invalid state
    with pytest.raises(ValueError):
        Address(
            street="123 Main St",
            city="Los Angeles",
            state="California",  # Should be 2-letter code
            zip="90210"
        )

def test_brand_colors_validation():
    """Test hex color validation."""
    # Valid colors
    colors = BrandColors(primary="#FF5733", secondary="#0066CC")
    assert colors.primary == "#FF5733"
    
    # Short form should be converted
    colors = BrandColors(primary="F57", secondary="06C")
    assert colors.primary == "#FF5577"
    
    # Invalid hex
    with pytest.raises(ValueError):
        BrandColors(primary="notahex", secondary="#0066CC")

def test_client_data_validation():
    """Test complete client data validation."""
    client = ClientData(
        practice_name="Test Practice",
        email="test@practice.com",
        phone="5551234567",
        terminology_preference="patients"
    )
    
    assert client.practice_name == "Test Practice"
    assert client.phone == "(555) 123-4567"  # Should be formatted
    assert client.terminology_preference == "patients"
