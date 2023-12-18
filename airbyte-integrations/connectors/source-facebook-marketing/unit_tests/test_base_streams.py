#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from functools import partial
from typing import Any, Iterable, Mapping

import pytest
from facebook_business import FacebookSession
from facebook_business.api import FacebookAdsApi, FacebookAdsApiBatch
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.base_streams import FBMarketingStream


@pytest.fixture(name="mock_batch_responses")
def mock_batch_responses_fixture(requests_mock):
    return partial(requests_mock.register_uri, "POST", f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/")


@pytest.fixture(name="batch")
def batch_fixture(api, mocker):
    batch = FacebookAdsApiBatch(api=api.api)
    mocker.patch.object(batch, "execute", wraps=batch.execute)
    mocker.patch.object(batch, "add_request", wraps=batch.add_request)
    mocker.patch.object(MyFacebookAdsApi, "new_batch", return_value=batch)
    return batch


class SomeTestStream(FBMarketingStream):
    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        yield from []


class TestDateTimeValue:
    def test_date_time_value(self):
        record = {
            "bla": "2023-01-19t20:38:59 0000",
            "created_time": "2023-01-19t20:38:59 0000",
            "creation_time": "2023-01-19t20:38:59 0000",
            "updated_time": "2023-01-19t20:38:59 0000",
            "event_time": "2023-01-19t20:38:59 0000",
            "first_fired_time": "2023-01-19t20:38:59 0000",
            "last_fired_time": "2023-01-19t20:38:59 0000",
            "sub_list": [
                {
                    "bla": "2023-01-19t20:38:59 0000",
                    "created_time": "2023-01-19t20:38:59 0000",
                    "creation_time": "2023-01-19t20:38:59 0000",
                    "updated_time": "2023-01-19t20:38:59 0000",
                    "event_time": "2023-01-19t20:38:59 0000",
                    "first_fired_time": "2023-01-19t20:38:59 0000",
                    "last_fired_time": "2023-01-19t20:38:59 0000",
                }
            ],
            "sub_entries1": {
                "sub_entries2": {
                    "bla": "2023-01-19t20:38:59 0000",
                    "created_time": "2023-01-19t20:38:59 0000",
                    "creation_time": "2023-01-19t20:38:59 0000",
                    "updated_time": "2023-01-19t20:38:59 0000",
                    "event_time": "2023-01-19t20:38:59 0000",
                    "first_fired_time": "2023-01-19t20:38:59 0000",
                    "last_fired_time": "2023-01-19t20:38:59 0000",
                }
            },
        }
        FBMarketingStream.fix_date_time(record)
        assert {
            "bla": "2023-01-19t20:38:59 0000",
            "created_time": "2023-01-19T20:38:59+0000",
            "creation_time": "2023-01-19T20:38:59+0000",
            "updated_time": "2023-01-19T20:38:59+0000",
            "event_time": "2023-01-19T20:38:59+0000",
            "first_fired_time": "2023-01-19T20:38:59+0000",
            "last_fired_time": "2023-01-19T20:38:59+0000",
            "sub_list": [
                {
                    "bla": "2023-01-19t20:38:59 0000",
                    "created_time": "2023-01-19T20:38:59+0000",
                    "creation_time": "2023-01-19T20:38:59+0000",
                    "updated_time": "2023-01-19T20:38:59+0000",
                    "event_time": "2023-01-19T20:38:59+0000",
                    "first_fired_time": "2023-01-19T20:38:59+0000",
                    "last_fired_time": "2023-01-19T20:38:59+0000",
                }
            ],
            "sub_entries1": {
                "sub_entries2": {
                    "bla": "2023-01-19t20:38:59 0000",
                    "created_time": "2023-01-19T20:38:59+0000",
                    "creation_time": "2023-01-19T20:38:59+0000",
                    "updated_time": "2023-01-19T20:38:59+0000",
                    "event_time": "2023-01-19T20:38:59+0000",
                    "first_fired_time": "2023-01-19T20:38:59+0000",
                    "last_fired_time": "2023-01-19T20:38:59+0000",
                }
            },
        } == record
