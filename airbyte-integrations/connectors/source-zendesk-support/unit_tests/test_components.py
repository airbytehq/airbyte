# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
import requests


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
def test_extraсtor_events(response_data, expected_events, components_module):
    # Create an instance of the extractor
    extractor = components_module.ZendeskSupportExtractorEvents()

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
def test_attribute_definitions_extractor(response_data, expected_records, components_module):
    # Create an instance of the extractor
    extractor = components_module.ZendeskSupportAttributeDefinitionsExtractor()

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


@pytest.mark.parametrize(
    "client_id, client_secret, refresh_token, expected_body",
    [
        (
            "test_client_id",
            "test_client_secret",
            "test_refresh_token",
            {
                "grant_type": "refresh_token",
                "refresh_token": "test_refresh_token",
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            },
        ),
    ],
)
def test_oauth_authenticator_refresh_request_body(client_id, client_secret, refresh_token, expected_body, components_module):
    """Test that the OAuth authenticator builds the correct refresh request body."""
    # Create an instance of the OAuth authenticator
    authenticator = components_module.ZendeskSupportOAuth2Authenticator(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        token_refresh_endpoint="https://test.zendesk.com/oauth/tokens",
        config={"subdomain": "test"},
        parameters={},
    )

    # Test the refresh request body
    request_body = authenticator.get_refresh_request_body()
    assert request_body == expected_body


@pytest.mark.parametrize(
    "response_json, expected_token, expected_expires_in, should_raise",
    [
        # Successful response with access token and expires_in
        ({"access_token": "new_access_token", "expires_in": 3600}, "new_access_token", 3600, False),
        # Response with access token but no expires_in (should default to 7200)
        ({"access_token": "new_access_token"}, "new_access_token", 7200, False),
        # Response without access token (should raise exception)
        ({"expires_in": 3600}, None, None, True),
        # Empty response (should raise exception)
        ({}, None, None, True),
    ],
)
def test_oauth_authenticator_refresh_access_token(response_json, expected_token, expected_expires_in, should_raise, components_module):
    """Test the OAuth access token refresh functionality."""
    import unittest.mock

    # Create an instance of the OAuth authenticator
    authenticator = components_module.ZendeskSupportOAuth2Authenticator(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token",
        token_refresh_endpoint="https://test.zendesk.com/oauth/tokens",
        config={"subdomain": "test"},
        parameters={},
    )

    # Mock the requests.request method
    with unittest.mock.patch("requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        if should_raise:
            with pytest.raises(Exception):
                authenticator.refresh_access_token()
        else:
            access_token, expires_in = authenticator.refresh_access_token()
            assert access_token == expected_token
            assert expires_in == expected_expires_in

            # Verify the request was made correctly
            mock_request.assert_called_once_with(
                method="POST",
                url="https://test.zendesk.com/oauth/tokens",
                json={
                    "grant_type": "refresh_token",
                    "refresh_token": "test_refresh_token",
                    "client_id": "test_client_id",
                    "client_secret": "test_client_secret",
                },
                headers={"Content-Type": "application/json"},
            )


def test_oauth_authenticator_refresh_http_error(components_module):
    """Test OAuth authenticator handles HTTP errors properly."""
    import unittest.mock

    # Create an instance of the OAuth authenticator
    authenticator = components_module.ZendeskSupportOAuth2Authenticator(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token",
        token_refresh_endpoint="https://test.zendesk.com/oauth/tokens",
        config={"subdomain": "test"},
        parameters={},
    )

    # Mock requests to raise an HTTP error
    with unittest.mock.patch("requests.request") as mock_request:
        mock_request.side_effect = requests.exceptions.RequestException("HTTP 401 Unauthorized")

        with pytest.raises(Exception) as exc_info:
            authenticator.refresh_access_token()

        assert "HTTP error while refreshing Zendesk access token" in str(exc_info.value)


def test_oauth_authenticator_refresh_json_error(components_module):
    """Test OAuth authenticator handles JSON parsing errors properly."""
    import unittest.mock

    # Create an instance of the OAuth authenticator
    authenticator = components_module.ZendeskSupportOAuth2Authenticator(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token",
        token_refresh_endpoint="https://test.zendesk.com/oauth/tokens",
        config={"subdomain": "test"},
        parameters={},
    )

    # Mock requests to return invalid JSON
    with unittest.mock.patch("requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            authenticator.refresh_access_token()

        assert "Invalid response format while refreshing Zendesk access token" in str(exc_info.value)
