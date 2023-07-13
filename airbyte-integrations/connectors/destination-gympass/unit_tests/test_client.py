#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, patch

from destination_gympass.client import GympassClient


def test_batch_write_is_called_with_expected_values():
    client = GympassClient(api_key="API_KEY")

    with patch("destination_gympass.client.requests.request") as mock_request:
        mock_request.return_value.status_code = 200

        keys_and_values = [{"key1": "value1"}, {"key2": "value2"}]
        client.batch_write(keys_and_values)

        mock_request.assert_called_once_with(
            method="POST",
            params=None,
            url="https://api.wellness.gympass.com/events",
            headers={"Accept": "application/json", "Authorization": "Bearer API_KEY"},
            json=keys_and_values,
        )


def test_get_events_url_returns_url():
    client = GympassClient(api_key="API_KEY")
    url = client._get_events_url()
    assert url == "https://api.wellness.gympass.com/events"


def test_get_auth_headers_returns_with_api_key():
    client = GympassClient(api_key="API_KEY")
    headers = client._get_auth_headers()
    assert headers == {"Authorization": "Bearer API_KEY"}


