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


def test_batching_record_filter_basic(mock_config, components_module):
    """Test BatchingRecordFilter accumulates IDs correctly."""
    record_filter = components_module.BatchingRecordFilter(
        config=mock_config,
        parameters={},
        batch_size=3,  # Small batch for testing
        id_field="id",
    )

    input_records = [
        {"id": "1", "name": "Deal 1"},
        {"id": "2", "name": "Deal 2"},
        {"id": "3", "name": "Deal 3"},
    ]

    batch_records = list(
        record_filter.filter_records(records=iter(input_records), stream_state={}, stream_slice=None, next_page_token=None)
    )

    # Should yield one batch record with all 3 IDs
    assert len(batch_records) == 1
    assert batch_records[0]["record_ids"] == [{"id": "1"}, {"id": "2"}, {"id": "3"}]


def test_batching_record_filter_multiple_batches(mock_config, components_module):
    """Test that filter yields multiple batches when exceeding batch_size."""
    record_filter = components_module.BatchingRecordFilter(config=mock_config, parameters={}, batch_size=1000, id_field="id")

    # Create 2500 records
    input_records = [{"id": str(i), "name": f"Record {i}"} for i in range(2500)]

    batch_records = list(
        record_filter.filter_records(records=iter(input_records), stream_state={}, stream_slice=None, next_page_token=None)
    )

    # Should yield 3 batches: 1000 + 1000 + 500
    assert len(batch_records) == 3
    assert len(batch_records[0]["record_ids"]) == 1000
    assert len(batch_records[1]["record_ids"]) == 1000
    assert len(batch_records[2]["record_ids"]) == 500

    # Verify IDs are in order
    assert batch_records[0]["record_ids"][0] == {"id": "0"}
    assert batch_records[0]["record_ids"][999] == {"id": "999"}
    assert batch_records[1]["record_ids"][0] == {"id": "1000"}
    assert batch_records[2]["record_ids"][0] == {"id": "2000"}
    assert batch_records[2]["record_ids"][499] == {"id": "2499"}


def test_batching_record_filter_partial_batch(mock_config, components_module):
    """Test that filter yields partial final batch."""
    record_filter = components_module.BatchingRecordFilter(config=mock_config, parameters={}, batch_size=10, id_field="id")

    # Create 25 records (2 full batches + 5 partial)
    input_records = [{"id": str(i)} for i in range(25)]

    batch_records = list(
        record_filter.filter_records(records=iter(input_records), stream_state={}, stream_slice=None, next_page_token=None)
    )

    assert len(batch_records) == 3
    assert len(batch_records[0]["record_ids"]) == 10
    assert len(batch_records[1]["record_ids"]) == 10
    assert len(batch_records[2]["record_ids"]) == 5


def test_batching_record_filter_empty_input(mock_config, components_module):
    """Test that filter handles empty input gracefully."""
    record_filter = components_module.BatchingRecordFilter(config=mock_config, parameters={}, batch_size=1000, id_field="id")

    batch_records = list(record_filter.filter_records(records=iter([]), stream_state={}, stream_slice=None, next_page_token=None))

    # Should yield no batches for empty input
    assert len(batch_records) == 0


def test_batching_record_filter_single_record(mock_config, components_module):
    """Test that filter yields a batch with a single record."""
    record_filter = components_module.BatchingRecordFilter(config=mock_config, parameters={}, batch_size=1000, id_field="id")

    input_records = [{"id": "123", "name": "Single Deal"}]

    batch_records = list(
        record_filter.filter_records(records=iter(input_records), stream_state={}, stream_slice=None, next_page_token=None)
    )

    assert len(batch_records) == 1
    assert batch_records[0]["record_ids"] == [{"id": "123"}]


def test_batching_record_filter_exact_batch_size(mock_config, components_module):
    """Test that filter handles exactly batch_size records."""
    record_filter = components_module.BatchingRecordFilter(config=mock_config, parameters={}, batch_size=100, id_field="id")

    # Create exactly 100 records
    input_records = [{"id": str(i)} for i in range(100)]

    batch_records = list(
        record_filter.filter_records(records=iter(input_records), stream_state={}, stream_slice=None, next_page_token=None)
    )

    # Should yield exactly 1 batch
    assert len(batch_records) == 1
    assert len(batch_records[0]["record_ids"]) == 100


def test_batching_record_filter_with_condition(mock_config, components_module):
    """Test that filter applies condition to filter records."""
    # Condition to only include records with id > 5
    record_filter = components_module.BatchingRecordFilter(
        config=mock_config, parameters={}, batch_size=10, id_field="id", condition="{{ record['id'] | int > 5 }}"
    )

    input_records = [{"id": str(i)} for i in range(10)]

    batch_records = list(
        record_filter.filter_records(records=iter(input_records), stream_state={}, stream_slice=None, next_page_token=None)
    )

    # Should only include IDs 6, 7, 8, 9 (4 records)
    assert len(batch_records) == 1
    assert len(batch_records[0]["record_ids"]) == 4
    assert batch_records[0]["record_ids"] == [{"id": "6"}, {"id": "7"}, {"id": "8"}, {"id": "9"}]


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
