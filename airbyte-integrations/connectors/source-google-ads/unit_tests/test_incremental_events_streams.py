#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.models import SyncMode
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import CampaignCriterion, ChangeStatus, cyclic_sieve

from .common import MockGoogleAdsClient as MockGoogleAdsClient


@pytest.fixture
def mock_ads_client(mocker, config):
    """Mock google ads library method, so it returns mocked Client"""
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict", return_value=MockGoogleAdsClient(config))


def mock_response_parent():
    yield [
        {"change_status.last_change_date_time": "2023-06-13 12:36:00.772447", "change_status.resource_type": "CAMPAIGN_CRITERION", "change_status.resource_status": "ADDED", "change_status.campaign_criterion": "1"},
        {"change_status.last_change_date_time": "2023-06-13 12:36:00.772447", "change_status.resource_type": "CAMPAIGN_CRITERION", "change_status.resource_status": "ADDED", "change_status.campaign_criterion": "2"},
        {"change_status.last_change_date_time": "2023-06-13 12:36:00.772447", "change_status.resource_type": "CAMPAIGN_CRITERION", "change_status.resource_status": "REMOVED", "change_status.campaign_criterion": "3"},
        {"change_status.last_change_date_time": "2023-06-13 12:36:00.772447", "change_status.resource_type": "CAMPAIGN_CRITERION", "change_status.resource_status": "REMOVED", "change_status.campaign_criterion": "4"},
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

    result = list(stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"], stream_slice=stream_slice))
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
    stream_state = {"change_status" : { customer_id : {  "change_status.last_change_date_time" : "2023-08-16 13:20:01.003295"}}}

    google_api = MockGoogleAds(credentials=config["credentials"])

    parent_stream = ChangeStatus(api=google_api, customers=customers)

    parent_stream.get_query = Mock()
    parent_stream.get_query.return_value = "query_parent"

    parent_stream.stream_slices = Mock()
    parent_stream.stream_slices.return_value = [parent_stream_slice]

    parent_stream.state = { customer_id : {  "change_status.last_change_date_time" : "2023-05-16 13:20:01.003295"}}

    stream = CampaignCriterion(api=google_api, customers=customers, parent_stream=parent_stream)
    stream.get_query = Mock()
    stream.get_query.return_value = "query_child"

    stream_slices = list(stream.stream_slices(stream_state=stream_state))

    assert stream_slices == [{'customer_id': '123', 'updated_ids': {'2', '1'}, 'deleted_ids': {'3', '4'}, 'id_to_time': {'1': '2023-06-13 12:36:00.772447', '2': '2023-06-13 12:36:00.772447', '3': '2023-06-13 12:36:00.772447', '4': '2023-06-13 12:36:00.772447'}}]

    result = list(stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"], stream_slice=stream_slices[0]))
    assert len(result) == 4

    deleted_record = {'change_status.last_change_date_time': '2023-06-13 12:36:00.772447', 'customer.id': None, 'campaign.id': None, 'campaign_criterion.resource_name': '3', 'campaign_criterion.campaign': None, 'campaign_criterion.age_range.type': None, 'campaign_criterion.mobile_application.name': None, 'campaign_criterion.negative': None, 'campaign_criterion.youtube_channel.channel_id': None, 'campaign_criterion.youtube_video.video_id': None}
    assert deleted_record in result

    assert stream.state == {'change_status': {'123': {'change_status.last_change_date_time': '2023-06-13'}}}

    assert stream.get_query.call_count == 1
