#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from requests import Response


@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
    }


@pytest.fixture
def mock_oauth_config():
    """Mock OAuth configuration for tests."""
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {
            "credentials_title": "OAuth Credentials",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "access_token": "test_access_token",
        },
    }


@pytest.mark.parametrize(
    "api_response, expected_records",
    [
        # Basic association with single type
        (
            {
                "results": [
                    {
                        "from": {"id": "123"},
                        "to": [{"toObjectId": 456, "associationTypes": [{"typeId": 3, "category": "HUBSPOT_DEFINED", "label": None}]}],
                    }
                ]
            },
            [{"from_id": "123", "to_id": "456", "association_type_id": 3, "category": "HUBSPOT_DEFINED", "label": None}],
        ),
        # Multiple associations with different types
        (
            {
                "results": [
                    {
                        "from": {"id": "100"},
                        "to": [
                            {
                                "toObjectId": 200,
                                "associationTypes": [
                                    {"typeId": 1, "category": "HUBSPOT_DEFINED", "label": None},
                                    {"typeId": 2, "category": "USER_DEFINED", "label": "Custom Label"},
                                ],
                            },
                            {"toObjectId": 300, "associationTypes": [{"typeId": 1, "category": "HUBSPOT_DEFINED", "label": None}]},
                        ],
                    }
                ]
            },
            [
                {"from_id": "100", "to_id": "200", "association_type_id": 1, "category": "HUBSPOT_DEFINED", "label": None},
                {"from_id": "100", "to_id": "200", "association_type_id": 2, "category": "USER_DEFINED", "label": "Custom Label"},
                {"from_id": "100", "to_id": "300", "association_type_id": 1, "category": "HUBSPOT_DEFINED", "label": None},
            ],
        ),
        # Empty response
        ({"results": []}, []),
        # From object with no associations
        ({"results": [{"from": {"id": "999"}, "to": []}]}, []),
    ],
    ids=["basic_single_association", "multiple_associations_and_types", "empty_response", "no_associations_for_object"],
)
def test_association_stream_extractor(api_response, expected_records, mock_config, components_module):
    """Test HubspotAssociationStreamExtractor extracts and flattens associations correctly."""
    extractor = components_module.HubspotAssociationStreamExtractor(
        from_object="deals", to_object="contacts", config=mock_config, parameters={}
    )

    # Mock response
    mock_response = Mock(spec=Response)
    mock_response.json.return_value = api_response

    # Extract records
    records = list(extractor.extract_records(mock_response))

    # Verify
    assert len(records) == len(expected_records)
    for record, expected in zip(records, expected_records):
        assert record == expected


def test_association_stream_extractor_string_ids(mock_config, components_module):
    """Test that extractor converts numeric IDs to strings for consistency."""
    api_response = {
        "results": [
            {
                "from": {"id": 123},  # numeric ID
                "to": [
                    {
                        "toObjectId": 456,  # numeric ID
                        "associationTypes": [{"typeId": 3, "category": "HUBSPOT_DEFINED", "label": None}],
                    }
                ],
            }
        ]
    }

    extractor = components_module.HubspotAssociationStreamExtractor(
        from_object="deals", to_object="contacts", config=mock_config, parameters={}
    )

    mock_response = Mock(spec=Response)
    mock_response.json.return_value = api_response

    records = list(extractor.extract_records(mock_response))

    assert len(records) == 1
    assert isinstance(records[0]["from_id"], str)
    assert isinstance(records[0]["to_id"], str)
    assert records[0]["from_id"] == "123"
    assert records[0]["to_id"] == "456"


def test_association_stream_extractor_with_labeled_associations(mock_config, components_module):
    """Test extraction of labeled (custom) associations."""
    api_response = {
        "results": [
            {
                "from": {"id": "deal_123"},
                "to": [{"toObjectId": 456, "associationTypes": [{"typeId": 100, "category": "USER_DEFINED", "label": "Primary Contact"}]}],
            }
        ]
    }

    extractor = components_module.HubspotAssociationStreamExtractor(
        from_object="deals", to_object="contacts", config=mock_config, parameters={}
    )

    mock_response = Mock(spec=Response)
    mock_response.json.return_value = api_response

    records = list(extractor.extract_records(mock_response))

    assert len(records) == 1
    assert records[0]["label"] == "Primary Contact"
    assert records[0]["category"] == "USER_DEFINED"
    assert records[0]["association_type_id"] == 100
