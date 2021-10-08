#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from unittest import TestCase

import requests_mock
import timeout_decorator
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException
from source_tiktok_marketing import SourceTiktokMarketing
from source_tiktok_marketing.streams import Advertisers

CONFIG_FILE = "secrets/config.json"


class TestTiktokMarketingSupport(TestCase):
    """This test class provides a set of tests for different TiktokMarketing streams.
    The TiktokMarketing API has difference pagination and sorting mechanisms for streams.
    Let's try to check them
    """

    @staticmethod
    def prepare_stream_args():
        """Generates streams settings from a file"""
        with open(CONFIG_FILE, "r") as f:
            return SourceTiktokMarketing._prepare_stream_args(json.loads(f.read()))

    @timeout_decorator.timeout(20)
    def test_backoff(self):
        """TiktokMarketing sends the header 'Retry-After' about needed delay.
        All streams have to handle it"""
        stream = Advertisers(**self.prepare_stream_args())
        with requests_mock.Mocker() as m:
            url = stream.url_base + stream.path()
            m.get(url, text=json.dumps({"code": 40100}))
            with self.assertRaises(UserDefinedBackoffException):
                list(stream.read_records(sync_mode=None))
