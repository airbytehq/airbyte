#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import pytest
from components import AdAccountRecordExtractor

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice

from .conftest import get_stream_by_name, read_from_stream


os.environ["REQUEST_CACHE_PATH"] = "/tmp"
_ANY_STREAM_NAME = "any_stream_name"
_RETRY_AFTER_HEADER = "XRetry-After"
_A_MAX_TIME = 10


def test_parse_response_with_sensitive_data(requests_mock, test_config):
    """Test that sensitive data is removed"""
    requests_mock.get(
        url="https://api.pinterest.com/v5/catalogs/feeds",
        json={"items": [{"id": "CatalogsFeeds1", "credentials": {"password": "bla"}}]},
    )
    actual_response = [
        record.record.data for record in read_from_stream(test_config, "catalogs_feeds", sync_mode=SyncMode.full_refresh).records
    ]
    assert actual_response == [{"id": "CatalogsFeeds1"}]


@pytest.mark.parametrize(
    ("stream_name", "stream_slice", "expected_path"),
    (
        ("boards", None, "boards"),
        ("ad_accounts", None, "ad_accounts"),
        ("board_sections", {"id": "123"}, "boards/123/sections"),
        ("board_pins", {"id": "123"}, "boards/123/pins"),
        ("board_section_pins", {"parent_slice": {"id": "234"}, "id": "123"}, "boards/234/sections/123/pins"),
        ("ad_account_analytics", {"id": "123"}, "ad_accounts/123/analytics"),
        ("campaigns", {"id": "123"}, "ad_accounts/123/campaigns"),
        (
            "campaign_analytics",
            {"parent_slice": {"id": "234"}, "id": "123"},
            "ad_accounts/234/campaigns/analytics?campaign_ids=123",
        ),
        ("ad_groups", {"id": "123"}, "ad_accounts/123/ad_groups"),
        (
            "ad_group_analytics",
            {"parent_slice": {"id": "234"}, "id": "123"},
            "ad_accounts/234/ad_groups/analytics?ad_group_ids=123",
        ),
        ("ads", {"id": "123"}, "ad_accounts/123/ads"),
        ("ad_analytics", {"parent_slice": {"id": "234"}, "id": "123"}, "ad_accounts/234/ads/analytics?ad_ids=123"),
        ("catalogs", None, "catalogs"),
        ("catalogs_feeds", None, "catalogs/feeds"),
        ("catalogs_product_groups", None, "catalogs/product_groups"),
        (
            "keywords",
            {"parent_slice": {"id": "AD_ACCOUNT_1"}, "id": "234"},
            "ad_accounts/AD_ACCOUNT_1/keywords?ad_group_id=234",
        ),
        ("audiences", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/audiences"),
        ("conversion_tags", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/conversion_tags"),
        ("customer_lists", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/customer_lists"),
    ),
)
def test_path(test_config, stream_name, stream_slice, expected_path):
    stream = get_stream_by_name(stream_name, test_config)
    if stream_slice:
        stream_slice = StreamSlice(partition=stream_slice, cursor_slice={})

    result = stream._stream_partition_generator._partition_factory._retriever.requester.get_path(
        stream_slice=stream_slice, stream_state=None, next_page_token=None
    )

    assert result == expected_path


def test_extract_records_with_items(test_response):
    extractor = AdAccountRecordExtractor()
    result = extractor.extract_records(test_response)
    assert result == test_response.json()["items"]


def test_extract_records_single_account(test_response_single_account):
    extractor = AdAccountRecordExtractor()
    result = extractor.extract_records(test_response_single_account)
    assert result == [{"id": "1234"}]
