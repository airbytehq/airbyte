#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import io
import json

import pytest
import requests
from source_iterable.components import EventsRecordExtractor, UsersRecordExtractor

from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonlDecoder


def test_events_extraction():
    mock_response = requests.Response()
    mock_response.raw = io.BytesIO(
        b'{"itblInternal": 1, "_type": "event", "createdAt": "2024-03-21", "email": "user@example.com", "data": {"event_type": "click"}}\n{"_type": "event", "createdAt": "2024-03-22", "data": {"event_type": "purchase"}}'
    )

    extractor = EventsRecordExtractor(
        field_path=[],
        decoder=JsonlDecoder(parameters={}),
        config={},
        parameters={},
    )
    records = list(extractor.extract_records(mock_response))

    assert len(records) == 2
    assert records[0] == {
        "_type": "event",
        "createdAt": "2024-03-21",
        "data": {"data": {"event_type": "click"}},
        "email": "user@example.com",
        "itblInternal": 1,
    }
    assert records[1] == {
        "_type": "event",
        "createdAt": "2024-03-22",
        "data": {"data": {"event_type": "purchase"}},
        "email": None,
        "itblInternal": None,
    }


@pytest.mark.parametrize(
    "input_record,expected_output",
    [
        pytest.param(
            {
                "email": "user@example.com",
                "userId": "u123",
                "itblUserId": "98765",
                "signupDate": "2024-01-15 10:30:00 +0000",
                "signupSource": "API",
                "profileUpdatedAt": "2024-06-01 08:00:00 +0000",
                "emailListIds": [1, 2, 3],
                "subscribedMessageTypeIds": [10],
                "unsubscribedMessageTypeIds": [20],
                "unsubscribedChannelIds": [30],
                "phoneNumber": "+15551234567",
                "country": "US",
                "locale": "en_US",
                "timeZone": "America/New_York",
                "itblInternal.emailDomain": "example.com",
                "itblInternal.documentCreatedAt": "2024-01-15 10:30:00 +0000",
                "itblInternal.documentUpdatedAt": "2024-06-01 08:00:00 +0000",
                "itblInternal.isUnknownUser": False,
                "itblDS.brandAffinityLabel": "loyal",
                "firstName": "Jane",
                "lastName": "Doe",
                "shopify_created_at": "2023-05-01T00:00:00Z",
                "aov": 42.5,
                "totalOrders": 7,
                "admin_graphql_api_id": "gid://shopify/Customer/123",
                "customField1": "value1",
            },
            {
                "email": "user@example.com",
                "userId": "u123",
                "itblUserId": "98765",
                "signupDate": "2024-01-15 10:30:00 +0000",
                "signupSource": "API",
                "profileUpdatedAt": "2024-06-01 08:00:00 +0000",
                "emailListIds": [1, 2, 3],
                "subscribedMessageTypeIds": [10],
                "unsubscribedMessageTypeIds": [20],
                "unsubscribedChannelIds": [30],
                "phoneNumber": "+15551234567",
                "country": "US",
                "locale": "en_US",
                "timeZone": "America/New_York",
                "itblInternal.emailDomain": "example.com",
                "itblInternal.documentCreatedAt": "2024-01-15 10:30:00 +0000",
                "itblInternal.documentUpdatedAt": "2024-06-01 08:00:00 +0000",
                "itblInternal.isUnknownUser": False,
                "itblDS.brandAffinityLabel": "loyal",
                "data": {
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "shopify_created_at": "2023-05-01T00:00:00Z",
                    "aov": 42.5,
                    "totalOrders": 7,
                    "admin_graphql_api_id": "gid://shopify/Customer/123",
                    "customField1": "value1",
                },
            },
            id="standard_fields_kept_custom_fields_in_data",
        ),
        pytest.param(
            {
                "email": "minimal@example.com",
                "profileUpdatedAt": "2024-03-01 00:00:00 +0000",
            },
            {
                "email": "minimal@example.com",
                "profileUpdatedAt": "2024-03-01 00:00:00 +0000",
                "data": {},
            },
            id="minimal_record_no_custom_fields",
        ),
        pytest.param(
            {
                "email": "custom-only@example.com",
                "addresses": [{"city": "NYC"}],
                "default_address": {"city": "NYC"},
                "ltr": 100,
                "boughtSas": True,
            },
            {
                "email": "custom-only@example.com",
                "data": {
                    "addresses": [{"city": "NYC"}],
                    "default_address": {"city": "NYC"},
                    "ltr": 100,
                    "boughtSas": True,
                },
            },
            id="shopify_specific_fields_moved_to_data",
        ),
        pytest.param(
            {
                "itblInternal.emailDomain": "test.io",
                "itblInternal.isUnknownUser": True,
                "itblInternal.newFutureField": "surprise",
            },
            {
                "itblInternal.emailDomain": "test.io",
                "itblInternal.isUnknownUser": True,
                "itblInternal.newFutureField": "surprise",
                "data": {},
            },
            id="all_itblInternal_dotted_keys_preserved",
        ),
    ],
)
def test_users_extraction(input_record, expected_output):
    mock_response = requests.Response()
    mock_response.raw = io.BytesIO(json.dumps(input_record).encode("utf-8"))

    extractor = UsersRecordExtractor(
        field_path=[],
        decoder=JsonlDecoder(parameters={}),
        config={},
        parameters={},
    )
    records = list(extractor.extract_records(mock_response))

    assert len(records) == 1
    assert records[0] == expected_output
