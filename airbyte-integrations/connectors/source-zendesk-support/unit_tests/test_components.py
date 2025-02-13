# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
import requests
from source_zendesk_support.components import (
    ZendeskSupportAttributeDefinitionsExtractor,
    ZendeskSupportExtractorEvents,
)


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
