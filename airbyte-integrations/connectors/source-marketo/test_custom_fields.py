#!/usr/bin/env python3
"""
Test script to validate custom fields support in Marketo Leads stream.
This script demonstrates how the dynamic schema generation works.
"""

import json
from unittest.mock import Mock, patch
from source_marketo.source import Leads


def test_dynamic_schema_generation():
    """Test that the Leads stream generates dynamic schema with custom fields."""
    
    # Mock configuration
    config = {
        "authenticator": Mock(),
        "domain_url": "https://test.mktorest.com",
        "start_date": "2023-01-01T00:00:00Z"
    }
    
    # Mock API response with standard and custom fields
    mock_api_response = {
        "result": [
            {
                "rest": {
                    "name": "id",
                    "displayName": "ID",
                    "dataType": "integer"
                }
            },
            {
                "rest": {
                    "name": "email",
                    "displayName": "Email Address",
                    "dataType": "email"
                }
            },
            {
                "rest": {
                    "name": "firstName",
                    "displayName": "First Name",
                    "dataType": "string"
                }
            },
            {
                "rest": {
                    "name": "lastName",
                    "displayName": "Last Name",
                    "dataType": "string"
                }
            },
            {
                "rest": {
                    "name": "customField1__c",
                    "displayName": "Custom Field 1",
                    "dataType": "string"
                }
            },
            {
                "rest": {
                    "name": "customScore__c",
                    "displayName": "Custom Score",
                    "dataType": "integer"
                }
            },
            {
                "rest": {
                    "name": "customDate__c",
                    "displayName": "Custom Date",
                    "dataType": "date"
                }
            },
            {
                "rest": {
                    "name": "customBoolean__c",
                    "displayName": "Custom Boolean",
                    "dataType": "boolean"
                }
            }
        ]
    }
    
    # Create Leads instance
    leads_stream = Leads(config)
    
    # Mock the session and API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    
    with patch.object(leads_stream, '_session') as mock_session:
        mock_session.get.return_value = mock_response
        mock_session.auth.get_auth_header.return_value = {"Authorization": "Bearer test_token"}
        
        # Test dynamic schema generation
        schema = leads_stream.get_json_schema()
        
        print("Generated Schema Properties:")
        print(json.dumps(list(schema["properties"].keys()), indent=2))
        
        # Verify custom fields are included
        assert "customField1__c" in schema["properties"]
        assert "customScore__c" in schema["properties"] 
        assert "customDate__c" in schema["properties"]
        assert "customBoolean__c" in schema["properties"]
        
        # Verify data types are correctly mapped
        assert schema["properties"]["customField1__c"]["type"] == ["string", "null"]
        assert schema["properties"]["customScore__c"]["type"] == ["integer", "null"]
        assert schema["properties"]["customDate__c"]["type"] == ["string", "null"]
        assert schema["properties"]["customDate__c"]["format"] == "date"
        assert schema["properties"]["customBoolean__c"]["type"] == ["boolean", "null"]
        
        # Test stream_fields property
        fields = leads_stream.stream_fields
        
        print("\nAvailable Fields for Extraction:")
        print(json.dumps(sorted(fields), indent=2))
        
        # Verify custom fields are included in extraction fields
        assert "customField1__c" in fields
        assert "customScore__c" in fields
        assert "customDate__c" in fields
        assert "customBoolean__c" in fields
        
        print("\n✅ All tests passed! Custom fields support is working correctly.")
        print(f"Total fields discovered: {len(fields)}")
        print(f"Custom fields found: {len([f for f in fields if '__c' in f])}")


def test_fallback_behavior():
    """Test that the implementation falls back gracefully when API fails."""
    
    config = {
        "authenticator": Mock(),
        "domain_url": "https://test.mktorest.com", 
        "start_date": "2023-01-01T00:00:00Z"
    }
    
    leads_stream = Leads(config)
    
    # Mock failed API response
    mock_response = Mock()
    mock_response.status_code = 500
    
    with patch.object(leads_stream, '_session') as mock_session:
        mock_session.get.return_value = mock_response
        mock_session.auth.get_auth_header.return_value = {"Authorization": "Bearer test_token"}
        
        # Mock the parent get_json_schema method
        with patch('source_marketo.source.MarketoExportBase.get_json_schema') as mock_parent:
            mock_parent.return_value = {"properties": {"id": {"type": "integer"}}}
            
            schema = leads_stream.get_json_schema()
            
            # Should fall back to parent schema
            mock_parent.assert_called_once()
            print("\n✅ Fallback behavior test passed!")


if __name__ == "__main__":
    print("Testing Marketo Custom Fields Implementation...")
    print("=" * 50)
    
    test_dynamic_schema_generation()
    test_fallback_behavior()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")
    print("\nThe Marketo Leads stream now supports:")
    print("• Dynamic discovery of custom fields")
    print("• Proper data type mapping")
    print("• Graceful fallback on API errors")
    print("• Automatic schema generation")
