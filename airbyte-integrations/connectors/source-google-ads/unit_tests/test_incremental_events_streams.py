#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from unittest.mock import DEFAULT, Mock, call

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils import AirbyteTracedException
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import CampaignCriterion, ChangeStatus

from .common import MockGoogleAdsClient as MockGoogleAdsClient


@pytest.fixture
def mock_ads_client(mocker, config):
    """Mock google ads library method, so it returns mocked Client"""
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict", return_value=MockGoogleAdsClient(config))


def mock_response_parent():
    yield [
        {"change_status.last_change_date_time": "2023-06-13 12:36:01.772447",
         "change_status.resource_type": "CAMPAIGN_CRITERION", "change_status.resource_status": "ADDED",
         "change_status.campaign_criterion": "1"},
        {"change_status.last_change_date_time": "2023-06-13 12:36:02.772447",
         "change_status.resource_type": "CAMPAIGN_CRITERION", "change_status.resource_status": "ADDED",
         "change_status.campaign_criterion": "2"},
        {"change_status.last_change_date_time": "2023-06-13 12:36:03.772447",
         "change_status.resource_type": "CAMPAIGN_CRITERION", "change_status.resource_status": "REMOVED",
         "change_status.campaign_criterion": "3"},
        {"change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
         "change_status.resource_type": "CAMPAIGN_CRITERION", "change_status.resource_status": "REMOVED",
         "change_status.campaign_criterion": "4"},
    ]


def mock_response_child():
    yield [
        {"customer.id": 123, "campaign.id": 1, "campaign_criterion.resource_name": "1"},
        {"customer.id": 123, "campaign.id": 1, "campaign_criterion.resource_name": "2"},
    ]


class MockGoogleAds(GoogleAds):
    def parse_single_result(self, schema, result):
        return result

    def send_request(self, query: str, customer_id: str):
        if query == "query_parent":
            return mock_response_parent()
        else:
            return mock_response_child()


def test_change_status_stream(mock_ads_client, config, customers):
    """
    """
    customer_id = next(iter(customers)).id
    stream_slice = {"customer_id": customer_id}

    google_api = MockGoogleAds(credentials=config["credentials"])

    stream = ChangeStatus(api=google_api, customers=customers)

    stream.get_query = Mock()
    stream.get_query.return_value = "query_parent"

    result = list(
        stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"],
                            stream_slice=stream_slice))
    assert len(result) == 4
    assert stream.get_query.call_count == 1
    stream.get_query.assert_called_with({"customer_id": customer_id})


def test_child_incremental_events_read(mock_ads_client, config, customers):
    """
    Page token expired while reading records on date 2021-01-03
    The latest read record is {"segments.date": "2021-01-03", "click_view.gclid": "4"}
    It should retry reading starting from 2021-01-03, already read records will be reread again from that date.
    It shouldn't read records on 2021-01-01, 2021-01-02
    """
    customer_id = next(iter(customers)).id
    parent_stream_slice = {"customer_id": customer_id, "resource_type": "CAMPAIGN_CRITERION"}
    stream_state = {
        "change_status": {customer_id: {"change_status.last_change_date_time": "2023-08-16 13:20:01.003295"}}}

    google_api = MockGoogleAds(credentials=config["credentials"])

    stream = CampaignCriterion(api=google_api, customers=customers)
    parent_stream = stream.parent_stream

    parent_stream.get_query = Mock()
    parent_stream.get_query.return_value = "query_parent"

    parent_stream.stream_slices = Mock()
    parent_stream.stream_slices.return_value = [parent_stream_slice]

    parent_stream.state = {customer_id: {"change_status.last_change_date_time": "2023-05-16 13:20:01.003295"}}

    stream.get_query = Mock()
    stream.get_query.return_value = "query_child"

    stream_slices = list(stream.stream_slices(stream_state=stream_state))

    assert stream_slices == [{'customer_id': '123', 'updated_ids': {'2', '1'}, 'deleted_ids': {'3', '4'},
                              'record_changed_time_map': {'1': '2023-06-13 12:36:01.772447', '2': '2023-06-13 12:36:02.772447',
                                                          '3': '2023-06-13 12:36:03.772447', '4': '2023-06-13 12:36:04.772447'}}]

    result = list(
        stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"],
                            stream_slice=stream_slices[0]))
    expected_result = [{'campaign.id': 1,
                        'campaign_criterion.resource_name': '1',
                        'change_status.last_change_date_time': '2023-06-13 12:36:01.772447',
                        'customer.id': 123},
                       {'campaign.id': 1,
                        'campaign_criterion.resource_name': '2',
                        'change_status.last_change_date_time': '2023-06-13 12:36:02.772447',
                        'customer.id': 123},
                       {'campaign_criterion.resource_name': '3',
                        'deleted_at': '2023-06-13 12:36:03.772447'},
                       {'campaign_criterion.resource_name': '4',
                        'deleted_at': '2023-06-13 12:36:04.772447'}]

    assert all([expected_row in result for expected_row in expected_result])

    assert stream.state == {'change_status': {'123': {'change_status.last_change_date_time': '2023-06-13 12:36:04.772447'}}}

    assert stream.get_query.call_count == 1


def mock_response_1():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:01.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "ADDED",
            "change_status.campaign_criterion": "1",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:02.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "ADDED",
            "change_status.campaign_criterion": "2",
        },
    ]


def mock_response_2():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:03.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "3",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "4",
        },
    ]


def mock_response_3():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "6",
        },
    ]


def mock_response_4():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "6",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "7",
        },
    ]


class MockGoogleAdsLimit(GoogleAds):
    count = 0

    def parse_single_result(self, schema, result):
        return result

    def send_request(self, query: str, customer_id: str):
        self.count += 1
        if self.count == 1:
            return mock_response_1()
        elif self.count == 2:
            return mock_response_2()
        else:
            return mock_response_3()


def mock_query_limit(self) -> int:
    return 2  # or whatever value you want for testing


def copy_call_args(mock):
    new_mock = Mock()

    def side_effect(*args, **kwargs):
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        new_mock(*args, **kwargs)
        return DEFAULT

    mock.side_effect = side_effect
    return new_mock


def test_query_limit_hit(mock_ads_client, config, customers):
    """
    Test the behavior of the `read_records` method in the `ChangeStatus` stream when the query limit is hit.

    This test simulates a scenario where the limit is hit and slice start_date is updated with latest record cursor
    """
    customer_id = next(iter(customers)).id
    stream_slice = {"customer_id": customer_id, "start_date": "2023-06-13 11:35:04.772447", "end_date": "2023-06-13 13:36:04.772447"}

    google_api = MockGoogleAdsLimit(credentials=config["credentials"])
    stream_config = dict(
        api=google_api,
        customers=customers,
    )
    stream = ChangeStatus(**stream_config)
    ChangeStatus.query_limit = property(mock_query_limit)
    stream.get_query = Mock(return_value="query")
    get_query_mock = copy_call_args(stream.get_query)

    result = list(
        stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"], stream_slice=stream_slice)
    )

    assert len(result) == 5
    assert stream.get_query.call_count == 3

    get_query_calls = [
        call({"customer_id": "123", "start_date": "2023-06-13 11:35:04.772447", "end_date": "2023-06-13 13:36:04.772447"}),
        call({"customer_id": "123", "start_date": "2023-06-13 12:36:02.772447", "end_date": "2023-06-13 13:36:04.772447"}),
        call({"customer_id": "123", "start_date": "2023-06-13 12:36:04.772447", "end_date": "2023-06-13 13:36:04.772447"}),
    ]

    get_query_mock.assert_has_calls(get_query_calls)


class MockGoogleAdsLimitException(MockGoogleAdsLimit):
    def send_request(self, query: str, customer_id: str):
        self.count += 1
        if self.count == 1:
            return mock_response_1()
        elif self.count == 2:
            return mock_response_2()
        elif self.count == 3:
            return mock_response_4()


def test_query_limit_hit_exception(mock_ads_client, config, customers):
    """
    Test the behavior of the `read_records` method in the `ChangeStatus` stream when the query limit is hit.

    This test simulates a scenario where the limit is hit and there are more than query_limit number of records with same cursor,
    then error will be raised
    """
    customer_id = next(iter(customers)).id
    stream_slice = {"customer_id": customer_id, "start_date": "2023-06-13 11:35:04.772447", "end_date": "2023-06-13 13:36:04.772447"}

    google_api = MockGoogleAdsLimitException(credentials=config["credentials"])
    stream_config = dict(
        api=google_api,
        customers=customers,
    )
    stream = ChangeStatus(**stream_config)
    ChangeStatus.query_limit = property(mock_query_limit)
    stream.get_query = Mock(return_value="query")

    with pytest.raises(AirbyteTracedException) as e:
        list(
            stream.read_records(
                sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"], stream_slice=stream_slice
            )
        )

    expected_message = "More then limit 2 records with same cursor field. Incremental sync is not possible for this stream."
    assert e.value.message == expected_message
