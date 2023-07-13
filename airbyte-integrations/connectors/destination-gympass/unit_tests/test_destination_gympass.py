#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, patch

from destination_gympass import DestinationGympass
from destination_gympass.client import GympassClient


def test_batch_write_posts_request_with_expected_values():
    gympass_client_mock = MagicMock()
    gympass_client_mock.BATCH_SIZE = 2

    input_messages = [
        {"type": "RECORD", "record": {"data": {"key1": "value1"}}},
        {"type": "RECORD", "record": {"data": {"key2": "value2"}}},
        {"type": "STATE"},
        {"type": "RECORD", "record": {"data": {"key3": "value3"}}},
    ]

    destination = GympassClient(api_key="API_KEY")
    destination.gympass_api_client = gympass_client_mock

    with patch("destination_gympass.client.GympassClient._request") as mock_request:
        mock_request.return_value.status_code = 200

        # Call batch_write function
        destination.batch_write(input_messages)

        # Assert batch_write function called _request with expected values
        mock_request.assert_called_with(
            http_method="POST",
            json=[{'type': 'RECORD', 'record': {'data': {'key1': 'value1'}}},
                  {'type': 'RECORD', 'record': {'data': {'key2': 'value2'}}}, {'type': 'STATE'},
                  {'type': 'RECORD', 'record': {'data': {'key3': 'value3'}}}],
        )


def test_destination_check_returns_success_for_expected_responses():
    logger_mock = MagicMock()
    config = {"api_key": "API_KEY"}

    with patch("destination_gympass.destination.requests.request") as mock_request:
        mock_request.return_value.status_code = 200

        destination = DestinationGympass()
        result = destination.check(logger_mock, config)

        assert result.status.name == "SUCCEEDED"

        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.wellness.gympass.com/events",
            headers={"Content-Type": "application/json", "Authorization": "Bearer API_KEY"},
            data="[{}]",
        )

    with patch("destination_gympass.destination.requests.request") as mock_request:
        mock_request.return_value.status_code = 400

        destination = DestinationGympass()
        result = destination.check(logger_mock, config)

        assert result.status.name == "SUCCEEDED"

        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.wellness.gympass.com/events",
            headers={"Content-Type": "application/json", "Authorization": "Bearer API_KEY"},
            data="[{}]",
        )

