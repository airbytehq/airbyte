# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from source_zendesk_support.components import (
    ZendeskSupportAttributeDefinitionsExtractor,
    ZendeskSupportAuditLogsIncrementalSync,
    ZendeskSupportExtractorEvents,
)


@pytest.mark.parametrize(
    "stream_state, stream_slice, next_page_token, expected_params",
    [
        (
            {},
            {"start_time": "2022-01-01T00:00:00Z", "end_time": "2022-01-02T00:00:00Z"},
            {},
            {"start_time_field": ["2022-01-01T00:00:00Z", "2022-01-02T00:00:00Z"]},
        ),
        ({}, {}, {}, {}),
    ],
)
def test_audit_logs_incremental_sync(mocker, stream_state, stream_slice, next_page_token, expected_params):
    # Instantiate the incremental sync class
    sync = ZendeskSupportAuditLogsIncrementalSync("2021-06-01T00:00:00Z", "updated_at", "%Y-%m-%dT%H:%M:%SZ", {}, {})

    # Setup mock for start_time_option.field_name.eval
    mock_field_name = mocker.MagicMock()
    mock_field_name.eval.return_value = "start_time_field"

    mock_start_time_option = mocker.MagicMock()
    mock_start_time_option.field_name = mock_field_name
    mock_start_time_option.inject_into = RequestOptionType.request_parameter

    # Setting up the injected options
    sync.start_time_option = mock_start_time_option
    sync.end_time_option = mock_start_time_option  # Assuming same field_name for simplicity

    # Patch eval methods to return appropriate field keys
    sync._partition_field_start = mocker.MagicMock()
    sync._partition_field_start.eval.return_value = "start_time"
    sync._partition_field_end = mocker.MagicMock()
    sync._partition_field_end.eval.return_value = "end_time"

    # Get the request parameters
    params = sync.get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    # Assert that params match the expected output
    assert params == expected_params, f"Expected params {expected_params}, but got {params}"


@pytest.mark.parametrize(
    "response_data, expected_events",
    [
        # Test case with no ticket_events in response
        ({"some_other_data": [{}]}, []),
        # Test case with empty ticket_events
        ({"ticket_events": []}, []),
        # Test case with ticket_events but no child_events
        ({"ticket_events": [{"via_reference_id": 123, "ticket_id": 456, "timestamp": "2022-01-01T00:00:00Z"}]}, []),
        # Test case with valid child_events and Comment event_type
        (
            {
                "ticket_events": [
                    {
                        "via_reference_id": 123,
                        "ticket_id": 456,
                        "timestamp": "2022-01-01T00:00:00Z",
                        "child_events": [{"event_type": "Comment", "via_reference_id": "unused", "via": {"some": "data"}}],
                    }
                ]
            },
            [
                {
                    "event_type": "Comment",
                    "via_reference_id": 123,
                    "ticket_id": 456,
                    "timestamp": "2022-01-01T00:00:00Z",
                    "via": {"some": "data"},
                }
            ],
        ),
        # Test case with an invalid 'via' property format
        (
            {
                "ticket_events": [
                    {
                        "via_reference_id": 123,
                        "ticket_id": 456,
                        "timestamp": "2022-01-01T00:00:00Z",
                        "child_events": [{"event_type": "Comment", "via_reference_id": "unused", "via": "incorrect_format"}],
                    }
                ]
            },
            [{"event_type": "Comment", "via_reference_id": 123, "ticket_id": 456, "timestamp": "2022-01-01T00:00:00Z", "via": None}],
        ),
    ],
)
def test_extraсtor_events(response_data, expected_events):
    # Create an instance of the extractor
    extractor = ZendeskSupportExtractorEvents()

    # Mock the response from requests
    response = MagicMock(spec=requests.Response)
    response.json.return_value = response_data

    # Invoke the extract_records method
    events = extractor.extract_records(response)

    # Assert that the returned events match the expected events
    assert events == expected_events, f"Expected events to be {expected_events}, but got {events}"


@pytest.mark.parametrize(
    "response_data, expected_records",
    [
        # Test case with both conditions_all and conditions_any properly filled
        (
            {"definitions": {"conditions_all": [{"id": 1}], "conditions_any": [{"id": 2}]}},
            [{"id": 1, "condition": "all"}, {"id": 2, "condition": "any"}],
        ),
        # Test case where conditions_all is empty
        ({"definitions": {"conditions_any": [{"id": 2}], "conditions_all": []}}, [{"id": 2, "condition": "any"}]),
        # Test case where conditions_any is empty
        ({"definitions": {"conditions_all": [{"id": 1}], "conditions_any": []}}, [{"id": 1, "condition": "all"}]),
        # Test case where both conditions are empty
        ({"definitions": {"conditions_all": [], "conditions_any": []}}, []),
        # Test case with malformed JSON (simulate JSONDecodeError)
        (None, []),  # This will be used to mock an exception in the response.json() call
    ],
)
def test_attribute_definitions_extractor(response_data, expected_records):
    # Create an instance of the extractor
    extractor = ZendeskSupportAttributeDefinitionsExtractor()

    # Mock the response from requests
    response = MagicMock(spec=requests.Response)
    if response_data is None:
        response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "", 0)
    else:
        response.json.return_value = response_data

    # Invoke the extract_records method
    records = extractor.extract_records(response)

    # Assert that the returned records match the expected records
    assert records == expected_records, f"Expected records to be {expected_records}, but got {records}"
