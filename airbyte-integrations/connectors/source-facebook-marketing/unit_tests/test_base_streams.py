#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from functools import partial
from typing import Any, Iterable, List, Mapping, Optional
from unittest.mock import MagicMock, PropertyMock

import pytest
from facebook_business import FacebookSession
from facebook_business.adobjects.abstractobject import AbstractObject
from facebook_business.api import FacebookAdsApi, FacebookAdsApiBatch, FacebookBadObjectError
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.base_streams import (
    FBMarketingIncrementalStream,
    FBMarketingReversedIncrementalStream,
    FBMarketingStream,
)

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.utils import AirbyteTracedException


@pytest.fixture(name="mock_batch_responses")
def mock_batch_responses_fixture(requests_mock):
    return partial(
        requests_mock.register_uri,
        "POST",
        f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/",
    )


@pytest.fixture(name="batch")
def batch_fixture(api, mocker):
    batch = FacebookAdsApiBatch(api=api.api)
    mocker.patch.object(batch, "execute", wraps=batch.execute)
    mocker.patch.object(batch, "add_request", wraps=batch.add_request)
    mocker.patch.object(MyFacebookAdsApi, "new_batch", return_value=batch)
    return batch


class SomeTestStream(FBMarketingStream):
    def list_objects(self, params: Mapping[str, Any], account_id: str = None) -> Iterable:
        yield from []


class ConcreteReversedStream(FBMarketingReversedIncrementalStream):
    cursor_field = "updated_time"

    def list_objects(self, params: Mapping[str, Any], account_id: str = None) -> Iterable:
        return []


class TestFieldsExceptions:
    """Tests for FBMarketingStream.fields() method with fields_exceptions filtering."""

    def test_fields_excludes_fields_exceptions(self, api, some_config):
        """Fields listed in fields_exceptions are excluded from the API request fields."""
        stream = SomeTestStream(api=api, account_ids=some_config["account_ids"])
        # Simulate a schema with several properties
        schema = {
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "rule": {"type": "object"},
                "status": {"type": "string"},
            }
        }
        stream.get_json_schema = lambda: schema

        # No exceptions: all fields returned
        stream.fields_exceptions = []
        stream._saved_fields = None
        stream.fields.cache_clear()
        assert sorted(stream.fields()) == ["id", "name", "rule", "status"]

        # With exceptions: 'rule' excluded (matches CustomAudiences behaviour)
        stream.fields_exceptions = ["rule"]
        stream._saved_fields = None
        stream.fields.cache_clear()
        result = stream.fields()
        assert "rule" not in result
        assert sorted(result) == ["id", "name", "status"]

    def test_fields_excludes_multiple_exceptions(self, api, some_config):
        """Multiple fields_exceptions are all excluded."""
        stream = SomeTestStream(api=api, account_ids=some_config["account_ids"])
        schema = {
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "rule": {"type": "object"},
                "extra": {"type": "string"},
            }
        }
        stream.get_json_schema = lambda: schema
        stream.fields_exceptions = ["rule", "extra"]
        stream._saved_fields = None
        stream.fields.cache_clear()
        result = stream.fields()
        assert sorted(result) == ["id", "name"]


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
    valid_statuses = ["ACTIVE", "PAUSED", "DELETED"]

    def list_objects(self, **kwargs):
        return []


@pytest.fixture
def incremental_class_instance(api):
    return ConcreteFBMarketingIncrementalStream(api=api, account_ids=["123", "456", "789"], start_date=None, end_date=None)


class TestFBMarketingStreamBadObjectError:
    """Tests for FacebookBadObjectError handling with retry in read_records."""

    def _make_stream(self, api, mocker, list_objects_side_effect):
        """Create a SomeTestStream with mocked list_objects."""
        mocker.patch.multiple(FBMarketingStream, __abstractmethods__=set())
        stream = SomeTestStream(api=api, account_ids=["123"])
        mocker.patch.object(stream, "list_objects", side_effect=list_objects_side_effect)
        return stream

    def test_read_records_succeeds(self, api, mocker):
        """Records are yielded lazily when list_objects succeeds."""
        records = [{"id": "1", "name": "rec1"}, {"id": "2", "name": "rec2"}]
        stream = self._make_stream(api, mocker, list_objects_side_effect=[records])

        result = list(
            stream.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_slice={"account_id": "123", "stream_state": {}},
            )
        )

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"
        assert all(r["account_id"] == "123" for r in result)

    def test_read_records_retries_on_bad_object_error(self, api, mocker):
        """read_records retries after FacebookBadObjectError and succeeds."""
        mocker.patch("source_facebook_marketing.streams.base_streams.time.sleep")
        records = [{"id": "1", "name": "rec1"}]
        stream = self._make_stream(
            api,
            mocker,
            list_objects_side_effect=[
                FacebookBadObjectError("Bad data"),
                records,
            ],
        )

        result = list(
            stream.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_slice={"account_id": "123", "stream_state": {}},
            )
        )

        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert stream.list_objects.call_count == 2

    def test_read_records_raises_traced_exception_after_max_retries(self, api, mocker):
        """read_records wraps FacebookBadObjectError in AirbyteTracedException after exhausting retries."""
        mocker.patch("source_facebook_marketing.streams.base_streams.time.sleep")
        stream = self._make_stream(
            api,
            mocker,
            list_objects_side_effect=[
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
            ],
        )

        with pytest.raises(AirbyteTracedException) as exc_info:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_slice={"account_id": "123", "stream_state": {}},
                )
            )

        assert exc_info.value.failure_type == FailureType.transient_error
        assert exc_info.value.internal_message == "Bad data"
        assert "inconsistent object data" in exc_info.value.message.lower()
        assert stream.list_objects.call_count == 5


class TestFBMarketingReversedStreamBadObjectError:
    """Tests for FacebookBadObjectError handling with retry in reversed stream read_records."""

    def _make_fb_object(self, data: dict) -> MagicMock:
        """Create a mock Facebook object that behaves like AbstractObject."""
        obj = MagicMock(spec=AbstractObject)
        obj.__getitem__ = lambda self_obj, key: data[key]
        obj.export_all_data.return_value = dict(data)
        return obj

    def _make_stream(self, api, mocker, list_objects_side_effect):
        """Create a ConcreteReversedStream with mocked list_objects."""
        mocker.patch.multiple(FBMarketingReversedIncrementalStream, __abstractmethods__=set())
        stream = ConcreteReversedStream(api=api, account_ids=["123"], start_date=None, end_date=None)
        mocker.patch.object(stream, "list_objects", side_effect=list_objects_side_effect)
        return stream

    def test_reversed_read_records_succeeds(self, api, mocker):
        """Records are yielded and cursor is updated on success."""
        fb_obj = self._make_fb_object({"id": "1", "updated_time": "2024-01-15"})
        stream = self._make_stream(api, mocker, list_objects_side_effect=[[fb_obj]])

        result = list(
            stream.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_slice={"account_id": "123", "stream_state": {}},
            )
        )

        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert stream._cursor_values["123"] == "2024-01-15"

    def test_reversed_read_records_retries_on_bad_object_error(self, api, mocker):
        """read_records retries after FacebookBadObjectError and succeeds."""
        mocker.patch("source_facebook_marketing.streams.base_streams.time.sleep")
        fb_obj = self._make_fb_object({"id": "1", "updated_time": "2024-01-15"})
        stream = self._make_stream(
            api,
            mocker,
            list_objects_side_effect=[
                FacebookBadObjectError("Bad data"),
                [fb_obj],
            ],
        )

        result = list(
            stream.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_slice={"account_id": "123", "stream_state": {}},
            )
        )

        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert stream.list_objects.call_count == 2
        assert stream._cursor_values["123"] == "2024-01-15"

    def test_reversed_read_records_raises_traced_exception_after_max_retries(self, api, mocker):
        """read_records wraps FacebookBadObjectError in AirbyteTracedException after exhausting retries."""
        mocker.patch("source_facebook_marketing.streams.base_streams.time.sleep")
        stream = self._make_stream(
            api,
            mocker,
            list_objects_side_effect=[
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
            ],
        )

        with pytest.raises(AirbyteTracedException) as exc_info:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_slice={"account_id": "123", "stream_state": {}},
                )
            )

        assert exc_info.value.failure_type == FailureType.transient_error
        assert stream.list_objects.call_count == 5

    def test_reversed_read_records_does_not_update_cursor_on_failure(self, api, mocker):
        """Cursor state is NOT updated when all retries are exhausted."""
        mocker.patch("source_facebook_marketing.streams.base_streams.time.sleep")
        stream = self._make_stream(
            api,
            mocker,
            list_objects_side_effect=[
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
                FacebookBadObjectError("Bad data"),
            ],
        )

        with pytest.raises(AirbyteTracedException):
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_slice={"account_id": "123", "stream_state": {}},
                )
            )

        assert "123" not in stream._cursor_values


class TestFBMarketingIncrementalStreamSliceAndState:
    def test_stream_slices_multiple_accounts_with_state(self, incremental_class_instance):
        stream_state = {
            "123": {"state_key": "state_value"},
            "456": {"state_key": "another_state_value"},
        }
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

    @pytest.mark.parametrize(
        "current_stream_state, latest_record, expected_state, instance_filter_statuses",
        [
            # Test case 1: State date is used because fewer filters are used
            (
                {"123": {"date": "2021-01-30T00:00:00+00:00", "include_deleted": True}, "include_deleted": True},
                {"account_id": "123", "date": "2021-01-20T00:00:00+00:00"},
                {
                    "123": {
                        "date": "2021-01-30T00:00:00+00:00",
                        "filter_statuses": ["ACTIVE"],
                        "include_deleted": True,
                    },
                    "include_deleted": True,
                },
                ["ACTIVE"],
            ),
            # Test case 2: State date is used because filter_statuses is the same as include_deleted
            (
                {"123": {"date": "2021-01-30T00:00:00+00:00", "include_deleted": True}, "include_deleted": True},
                {"account_id": "123", "date": "2021-01-20T00:00:00+00:00"},
                {
                    "123": {
                        "date": "2021-01-30T00:00:00+00:00",
                        "filter_statuses": ["ACTIVE", "PAUSED", "DELETED"],
                        "include_deleted": True,
                    },
                    "include_deleted": True,
                },
                ["ACTIVE", "PAUSED", "DELETED"],
            ),
            # Test case 3: State date is used because filter_statuses is the same as include_deleted
            (
                {
                    "123": {
                        "date": "2023-02-15T00:00:00+00:00",
                        "include_deleted": False,
                    }
                },
                {"account_id": "123", "date": "2021-01-20T00:00:00+00:00"},
                {
                    "123": {
                        "date": "2023-02-15T00:00:00+00:00",
                        "filter_statuses": [],
                        "include_deleted": False,
                    }
                },
                [],
            ),
            # Test case 4: State date is ignored because there are more filters in the new config
            (
                {
                    "123": {
                        "date": "2023-02-15T00:00:00+00:00",
                        "include_deleted": False,
                    }
                },
                {"account_id": "123", "date": "2021-01-20T00:00:00+00:00"},
                {
                    "123": {
                        "date": "2021-01-20T00:00:00+00:00",
                        "filter_statuses": ["ACTIVE", "PAUSED"],
                        "include_deleted": False,
                    }
                },
                ["ACTIVE", "PAUSED"],
            ),
            # Test case 5: Mismatching filter_statuses with include_deleted false
            (
                {
                    "123": {
                        "date": "2023-02-15T00:00:00+00:00",
                        "filter_statuses": ["PAUSED"],
                        "include_deleted": False,
                    }
                },
                {"account_id": "123", "date": "2021-01-20T00:00:00+00:00"},
                {
                    "123": {
                        "date": "2021-01-20T00:00:00+00:00",
                        "filter_statuses": ["ACTIVE"],
                        "include_deleted": False,
                    }
                },
                ["ACTIVE"],
            ),
            # Test case 6: No filter_statuses or include_deleted in state, instance has filter_statuses
            (
                {"123": {"date": "2023-02-15T00:00:00+00:00"}},
                {"account_id": "123", "date": "2021-01-20T00:00:00+00:00"},
                {
                    "123": {
                        "date": "2021-01-20T00:00:00+00:00",
                        "filter_statuses": ["ACTIVE"],
                    }
                },
                ["ACTIVE"],
            ),
        ],
    )
    def test_get_updated_state(
        self,
        incremental_class_instance,
        current_stream_state,
        latest_record,
        expected_state,
        instance_filter_statuses,
    ):
        # Set the instance's filter_statuses
        incremental_class_instance._filter_statuses = instance_filter_statuses

        new_state = incremental_class_instance._get_updated_state(current_stream_state, latest_record)
        assert new_state == expected_state
