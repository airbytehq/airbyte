# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, patch

import pytest
from source_freshdesk.components import FreshdeskRequester, FreshdeskTicketsIncrementalRequester


@pytest.mark.parametrize(
    "requests_per_minute, expected_call_credit_cost",
    [
        (None, None),  # No call to CallCredit.consume expected when requests_per_minute is None
        (60, 1),  # CallCredit.consume called with cost 1 when requests_per_minute is set
    ],
)
def test_sends_request_with_default_parameters_and_receives_response(requests_per_minute, expected_call_credit_cost):
    config = {"requests_per_minute": requests_per_minute} if requests_per_minute is not None else {}
    parameters = {}

    # Patch CallCredit to monitor calls to its consume method
    with patch("source_freshdesk.components.CallCredit") as MockCallCredit:
        mock_call_credit_instance = MagicMock()
        MockCallCredit.return_value = mock_call_credit_instance

        requester = FreshdeskRequester(
            name="agents", url_base="https://freshdesk.com", path="/api/v2", parameters=parameters, config=config
        )

        # Patch the HttpRequester.send_request to prevent actual HTTP requests
        with patch("source_freshdesk.components.HttpRequester.send_request", return_value=MagicMock()):
            response = requester.send_request()

        # If requests_per_minute is None, _call_credit should not be created, thus CallCredit.consume should not be called
        if expected_call_credit_cost is None:
            mock_call_credit_instance.consume.assert_not_called()
        else:
            mock_call_credit_instance.consume.assert_called_once_with(expected_call_credit_cost)

        assert response is not None


@pytest.mark.parametrize(
    "request_params, expected_modified_params, expected_call_credit_cost, requests_per_minute, consume_expected",
    [
        ({"page": "1991-08-24"}, {}, 3, 60, True),  # Rate limiting applied, expect _call_credit.consume to be called
        ({"page": 1}, {"page": 1}, 3, 60, True),  # Rate limiting applied, expect _call_credit.consume to be called
        ({"page": "1991-08-24"}, {}, 3, None, False),  # No rate limiting, do not expect _call_credit.consume to be called
        ({"page": 1}, {"page": 1}, 3, None, False),  # No rate limiting, do not expect _call_credit.consume to be called
    ],
)
def test_freshdesk_tickets_incremental_requester_send_request(
    request_params, expected_modified_params, expected_call_credit_cost, requests_per_minute, consume_expected
):
    config = {"requests_per_minute": requests_per_minute} if requests_per_minute is not None else {}

    # Mock CallCredit to monitor calls to its consume method
    with patch("source_freshdesk.components.CallCredit") as mock_call_credit:
        mock_call_credit_instance = MagicMock()
        mock_call_credit.return_value = mock_call_credit_instance

        # Initialize the requester with mock config
        requester = FreshdeskTicketsIncrementalRequester(
            name="tickets", url_base="https://example.com", path="/api/v2/tickets", parameters={}, config=config
        )

        # Patch the HttpRequester.send_request to prevent actual HTTP requests
        with patch("source_freshdesk.components.HttpRequester.send_request", return_value=MagicMock()) as mock_super_send_request:
            # Call send_request with test parameters
            requester.send_request(request_params=request_params)

            # Check if _consume_credit was correctly handled based on requests_per_minute
            if consume_expected:
                mock_call_credit_instance.consume.assert_called_once_with(expected_call_credit_cost)
            else:
                mock_call_credit_instance.consume.assert_not_called()

            # Check if HttpRequester.send_request was called with the modified request_params
            mock_super_send_request.assert_called_once_with(request_params=expected_modified_params)
