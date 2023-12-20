#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from functools import partial
from typing import Any, Iterable, Mapping

import pytest
from facebook_business import FacebookSession
from facebook_business.api import FacebookAdsApi, FacebookAdsApiBatch
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.base_streams import FBMarketingIncrementalStream, FBMarketingStream


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


class ConcreteFBMarketingIncrementalStream(FBMarketingIncrementalStream):
    cursor_field = "date"

    def list_objects(self, **kwargs):
        return []


@pytest.fixture
def incremental_class_instance(api):
    return ConcreteFBMarketingIncrementalStream(api=api, account_ids=["123", "456", "789"], start_date=None, end_date=None)


class TestFBMarketingIncrementalStreamSliceAndState:
    def test_stream_slices_multiple_accounts_with_state(self, incremental_class_instance):
        stream_state = {"123": {"state_key": "state_value"}, "456": {"state_key": "another_state_value"}}
        expected_slices = [
            {"account_id": "123", "stream_state": {"state_key": "state_value"}},
            {"account_id": "456", "stream_state": {"state_key": "another_state_value"}},
            {"account_id": "789", "stream_state": {}},
        ]
        assert list(incremental_class_instance.stream_slices(stream_state)) == expected_slices

    def test_stream_slices_multiple_accounts_empty_state(self, incremental_class_instance):
        expected_slices = [
            {"account_id": "123", "stream_state": {}},
            {"account_id": "456", "stream_state": {}},
            {"account_id": "789", "stream_state": {}},
        ]
        assert list(incremental_class_instance.stream_slices()) == expected_slices

    def test_stream_slices_single_account_with_state(self, incremental_class_instance):
        incremental_class_instance._account_ids = ["123"]
        stream_state = {"state_key": "state_value"}
        expected_slices = [{"account_id": "123", "stream_state": stream_state}]
        assert list(incremental_class_instance.stream_slices(stream_state)) == expected_slices

    def test_stream_slices_single_account_empty_state(self, incremental_class_instance):
        incremental_class_instance._account_ids = ["123"]
        expected_slices = [{"account_id": "123", "stream_state": None}]
        assert list(incremental_class_instance.stream_slices()) == expected_slices

    def test_get_updated_state(self, incremental_class_instance):
        current_stream_state = {"123": {"date": "2021-01-15T00:00:00+00:00"}, "include_deleted": False}
        latest_record = {"account_id": "123", "date": "2021-01-20T00:00:00+00:00"}

        expected_state = {"123": {"date": "2021-01-20T00:00:00+00:00", "include_deleted": False}, "include_deleted": False}

        new_state = incremental_class_instance.get_updated_state(current_stream_state, latest_record)
        assert new_state == expected_state
