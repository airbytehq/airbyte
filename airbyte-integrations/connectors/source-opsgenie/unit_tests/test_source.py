#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock

import responses
from source_opsgenie.source import SourceOpsgenie


class SourceOpsgenieTest(unittest.TestCase):
    def test_stream_count(self):
        source = SourceOpsgenie()
        config_mock = MagicMock()
        streams = source.streams(config_mock)
        expected_streams_number = 9
        self.assertEqual(len(streams), expected_streams_number)

    @responses.activate
    def test_check_connection(self):
        log_mock, _ = MagicMock(), MagicMock()
        source = SourceOpsgenie()

        sample_account = {
            "data": {"name": "opsgenie", "userCount": 1450, "plan": {"maxUserCount": 1500, "name": "Enterprise", "isYearly": True}},
            "took": 0.084,
            "requestId": "e5122017-f5c5-4681-88ec-84e2898a61ad",
        }

        responses.add("GET", "https://api.opsgenie.com/v2/account", json=sample_account)

        (success, err) = source.check_connection(log_mock, {"endpoint": "api.opsgenie.com", "api_token": "123"})
        self.assertTrue(success)
        self.assertIsNone(err)
