#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import pytest
from google.ads.googleads.v17.services.types.google_ads_service import GoogleAdsRow
from source_google_ads.source import SourceGoogleAds

from airbyte_cdk.models import SyncMode


@pytest.fixture(scope="module")
def config():
    with open(Path(__file__).parent.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())


@pytest.fixture(scope="module")
def streams(config):
    return SourceGoogleAds().streams(config=config)


@pytest.fixture(scope="module")
def customer_label(streams):
    return next(filter(lambda s: s.name == "customer_label", streams))


@pytest.fixture(scope="module")
def topic_view(streams):
    return next(filter(lambda s: s.name == "topic_view", streams))


@pytest.fixture(scope="module")
def shopping_performance_view(streams):
    return next(filter(lambda s: s.name == "shopping_performance_view", streams))


def create_google_ads_row_from_dict(data: dict) -> GoogleAdsRow:
    row = GoogleAdsRow()

    for key, value in data.items():
        parts = key.split(".")
        current_obj = row

        for part in parts[:-1]:
            current_obj = getattr(current_obj, part)

        setattr(current_obj, parts[-1], value)

    return row


@pytest.mark.parametrize(
    "stream_fixture_name, expected_records",
    [
        (
            "customer_label",
            [
                {
                    "customer_label.resource_name": "123",
                    "customer_label.customer": "customer",
                    "customer.id": 123,
                    "customer_label.label": "customer_label",
                },
                {
                    "customer_label.resource_name": "1234",
                    "customer_label.customer": "customer",
                    "customer.id": 123,
                    "customer_label.label": "customer_label1",
                },
            ],
        ),
        (
            "topic_view",
            [
                {
                    "topic_view.resource_name": "customers/4651612872/topicViews/144799120517~945751797",
                    "customer.currency_code": "USD",
                    "customer.descriptive_name": "Airbyte",
                    "customer.time_zone": "America/Los_Angeles",
                    "metrics.active_view_cpm": 264196.96969696967,
                    "metrics.active_view_ctr": 0.0,
                    "metrics.active_view_impressions": 66,
                    "metrics.active_view_measurability": 1.0,
                    "metrics.active_view_measurable_cost_micros": 17437,
                    "metrics.active_view_measurable_impressions": 90,
                    "metrics.active_view_viewability": 0.7333333333333333,
                    "ad_group.id": 144799120517,
                    "ad_group.name": "Ad group 1",
                    "ad_group.status": "ENABLED",
                    "segments.ad_network_type": "CONTENT",
                    "metrics.all_conversions_from_interactions_rate": 0.0,
                    "metrics.all_conversions_value": 0.0,
                    "metrics.all_conversions": 0.0,
                    "metrics.average_cost": 0.0,
                    "metrics.average_cpc": 0.0,
                    "metrics.average_cpe": 0.0,
                    "metrics.average_cpm": 193744.44444444444,
                    "metrics.average_cpv": 0.0,
                    "ad_group.base_ad_group": "customers/4651612872/adGroups/144799120517",
                    "campaign.base_campaign": "customers/4651612872/campaigns/19410069806",
                    "ad_group_criterion.bid_modifier": 0.0,
                    "campaign.bidding_strategy": "",
                    "campaign.bidding_strategy_type": "MANUAL_CPM",
                    "campaign.id": 19410069806,
                    "campaign.name": "Brand awareness and reach-Display-1",
                    "campaign.status": "PAUSED",
                    "metrics.clicks": 0,
                    "metrics.conversions_from_interactions_rate": 0.0,
                    "metrics.conversions_value": 0.0,
                    "metrics.conversions": 0.0,
                    "metrics.cost_micros": 17437,
                    "metrics.cost_per_all_conversions": 0.0,
                    "metrics.cost_per_conversion": 0.0,
                    "ad_group_criterion.effective_cpc_bid_micros": 10000,
                    "ad_group_criterion.effective_cpc_bid_source": "AD_GROUP",
                    "ad_group_criterion.effective_cpm_bid_micros": 2000000,
                    "ad_group_criterion.effective_cpm_bid_source": "AD_GROUP",
                    "ad_group_criterion.topic.path": ["", "Online Communities"],
                    "metrics.cross_device_conversions": 0.0,
                    "metrics.ctr": 0.0,
                    "segments.date": "2024-01-03",
                    "segments.day_of_week": "WEDNESDAY",
                    "segments.device": "DESKTOP",
                    "metrics.engagement_rate": 0.0,
                    "metrics.engagements": 0,
                    "customer.id": 4651612872,
                    "ad_group_criterion.final_mobile_urls": [],
                    "ad_group_criterion.final_urls": [],
                    "metrics.gmail_forwards": 0,
                    "metrics.gmail_saves": 0,
                    "metrics.gmail_secondary_clicks": 0,
                    "ad_group_criterion.criterion_id": 945751797,
                    "metrics.impressions": 90,
                    "metrics.interaction_rate": 0.0,
                    "metrics.interaction_event_types": [],
                    "metrics.interactions": 0,
                    "ad_group_criterion.negative": False,
                    "ad_group.targeting_setting.target_restrictions": [],
                    "segments.month": "2024-01-01",
                    "segments.quarter": "2024-01-01",
                    "ad_group_criterion.status": "ENABLED",
                    "ad_group_criterion.tracking_url_template": "",
                    "ad_group_criterion.url_custom_parameters": [],
                    "metrics.value_per_all_conversions": 0.0,
                    "metrics.value_per_conversion": 0.0,
                    "ad_group_criterion.topic.topic_constant": "topicConstants/299",
                    "metrics.video_quartile_p100_rate": 0.0,
                    "metrics.video_quartile_p25_rate": 0.0,
                    "metrics.video_quartile_p50_rate": 0.0,
                    "metrics.video_quartile_p75_rate": 0.0,
                    "metrics.video_view_rate": 0.0,
                    "metrics.video_views": 0,
                    "metrics.view_through_conversions": 0,
                    "segments.week": "2024-01-01",
                    "segments.year": 2024,
                },
                {
                    "topic_view.resource_name": "customers/4651612872/topicViews/144799120517~1543464477",
                    "customer.currency_code": "USD",
                    "customer.descriptive_name": "Airbyte",
                    "customer.time_zone": "America/Los_Angeles",
                    "metrics.active_view_cpm": 862000.0,
                    "metrics.active_view_ctr": 0.0,
                    "metrics.active_view_impressions": 2,
                    "metrics.active_view_measurability": 1.0,
                    "metrics.active_view_measurable_cost_micros": 1724,
                    "metrics.active_view_measurable_impressions": 4,
                    "metrics.active_view_viewability": 0.5,
                    "ad_group.id": 144799120517,
                    "ad_group.name": "Ad group 1",
                    "ad_group.status": "ENABLED",
                    "segments.ad_network_type": "CONTENT",
                    "metrics.all_conversions_from_interactions_rate": 0.0,
                    "metrics.all_conversions_value": 0.0,
                    "metrics.all_conversions": 0.0,
                    "metrics.average_cost": 0.0,
                    "metrics.average_cpc": 0.0,
                    "metrics.average_cpe": 0.0,
                    "metrics.average_cpm": 431000.0,
                    "metrics.average_cpv": 0.0,
                    "ad_group.base_ad_group": "customers/4651612872/adGroups/144799120517",
                    "campaign.base_campaign": "customers/4651612872/campaigns/19410069806",
                    "ad_group_criterion.bid_modifier": 0.0,
                    "campaign.bidding_strategy": "",
                    "campaign.bidding_strategy_type": "MANUAL_CPM",
                    "campaign.id": 19410069806,
                    "campaign.name": "Brand awareness and reach-Display-1",
                    "campaign.status": "PAUSED",
                    "metrics.clicks": 0,
                    "metrics.conversions_from_interactions_rate": 0.0,
                    "metrics.conversions_value": 0.0,
                    "metrics.conversions": 0.0,
                    "metrics.cost_micros": 1724,
                    "metrics.cost_per_all_conversions": 0.0,
                    "metrics.cost_per_conversion": 0.0,
                    "ad_group_criterion.effective_cpc_bid_micros": 10000,
                    "ad_group_criterion.effective_cpc_bid_source": "AD_GROUP",
                    "ad_group_criterion.effective_cpm_bid_micros": 2000000,
                    "ad_group_criterion.effective_cpm_bid_source": "AD_GROUP",
                    "ad_group_criterion.topic.path": ["", "Shopping"],
                    "metrics.cross_device_conversions": 0.0,
                    "metrics.ctr": 0.0,
                    "segments.date": "2024-01-03",
                    "segments.day_of_week": "WEDNESDAY",
                    "segments.device": "DESKTOP",
                    "metrics.engagement_rate": 0.0,
                    "metrics.engagements": 0,
                    "customer.id": 4651612872,
                    "ad_group_criterion.final_mobile_urls": [],
                    "ad_group_criterion.final_urls": [],
                    "metrics.gmail_forwards": 0,
                    "metrics.gmail_saves": 0,
                    "metrics.gmail_secondary_clicks": 0,
                    "ad_group_criterion.criterion_id": 1543464477,
                    "metrics.impressions": 4,
                    "metrics.interaction_rate": 0.0,
                    "metrics.interaction_event_types": [],
                    "metrics.interactions": 0,
                    "ad_group_criterion.negative": False,
                    "ad_group.targeting_setting.target_restrictions": [],
                    "segments.month": "2024-01-01",
                    "segments.quarter": "2024-01-01",
                    "ad_group_criterion.status": "ENABLED",
                    "ad_group_criterion.tracking_url_template": "",
                    "ad_group_criterion.url_custom_parameters": [],
                    "metrics.value_per_all_conversions": 0.0,
                    "metrics.value_per_conversion": 0.0,
                    "ad_group_criterion.topic.topic_constant": "topicConstants/18",
                    "metrics.video_quartile_p100_rate": 0.0,
                    "metrics.video_quartile_p25_rate": 0.0,
                    "metrics.video_quartile_p50_rate": 0.0,
                    "metrics.video_quartile_p75_rate": 0.0,
                    "metrics.video_view_rate": 0.0,
                    "metrics.video_views": 0,
                    "metrics.view_through_conversions": 0,
                    "segments.week": "2024-01-01",
                    "segments.year": 2024,
                },
            ],
        ),
        (
            "shopping_performance_view",
            [
                {
                    "customer.descriptive_name": "Customer ABC",
                    "ad_group.id": 12345,
                    "ad_group.name": "Ad Group 1",
                    "ad_group.status": "REMOVED",
                    "segments.ad_network_type": "UNKNOWN",
                    "segments.product_aggregator_id": 67890,
                    "metrics.all_conversions_from_interactions_rate": 0.75,
                    "metrics.all_conversions_value": 150.25,
                    "metrics.all_conversions": 5.0,
                    "metrics.average_cpc": 0.5,
                    "segments.product_brand": "Brand XYZ",
                    "campaign.id": 11112,
                    "campaign.name": "Campaign 1",
                    "campaign.status": "UNKNOWN",
                    "segments.product_category_level1": "Electronics",
                    "segments.product_category_level2": "Mobile Phones",
                    "segments.product_category_level3": "Smartphones",
                    "segments.product_category_level4": "Android",
                    "segments.product_category_level5": "Samsung",
                    "segments.product_channel": "UNSPECIFIED",
                    "segments.product_channel_exclusivity": "SINGLE_CHANNEL",
                    "segments.click_type": "APP_DEEPLINK",
                    "metrics.clicks": 10,
                    "metrics.conversions_from_interactions_rate": 0.5,
                    "metrics.conversions_value": 100.5,
                    "metrics.conversions": 4.0,
                    "metrics.cost_micros": 5000000,
                    "metrics.cost_per_all_conversions": 25.05,
                    "metrics.cost_per_conversion": 6.25,
                    "segments.product_country": "US",
                    "metrics.cross_device_conversions": 2.0,
                    "metrics.ctr": 0.1,
                    "segments.product_custom_attribute0": "Attribute 0",
                    "segments.product_custom_attribute1": "Attribute 1",
                    "segments.product_custom_attribute2": "Attribute 2",
                    "segments.product_custom_attribute3": "Attribute 3",
                    "segments.product_custom_attribute4": "Attribute 4",
                    "segments.date": "2023-09-22",
                    "segments.day_of_week": "FRIDAY",
                    "segments.device": "TABLET",
                    "customer.id": 123,
                    "metrics.impressions": 100,
                    "segments.product_language": "English",
                    "segments.product_merchant_id": 54321,
                    "segments.month": "September",
                    "segments.product_item_id": "ITEM123",
                    "segments.product_condition": 2,
                    "segments.product_title": "Samsung Galaxy S23",
                    "segments.product_type_l1": "Electronics",
                    "segments.product_type_l2": "Phones",
                    "segments.product_type_l3": "Smartphones",
                    "segments.product_type_l4": "Android",
                    "segments.product_type_l5": "Samsung",
                    "segments.quarter": "Q3",
                    "segments.product_store_id": "STORE123",
                    "metrics.value_per_all_conversions": 30.05,
                    "metrics.value_per_conversion": 7.5,
                    "segments.week": "38",
                    "segments.year": 2023,
                },
                {
                    "customer.descriptive_name": "Customer ABC",
                    "ad_group.id": 12345,
                    "ad_group.name": "Ad Group 1",
                    "ad_group.status": "REMOVED",
                    "segments.ad_network_type": "UNKNOWN",
                    "segments.product_aggregator_id": 67890,
                    "metrics.all_conversions_from_interactions_rate": 0.75,
                    "metrics.all_conversions_value": 150.25,
                    "metrics.all_conversions": 5.0,
                    "metrics.average_cpc": 0.5,
                    "segments.product_brand": "Brand XYZ",
                    "campaign.id": 11112,
                    "campaign.name": "Campaign 1",
                    "campaign.status": "UNKNOWN",
                    "segments.product_category_level1": "Electronics",
                    "segments.product_category_level2": "Mobile Phones",
                    "segments.product_category_level3": "Smartphones",
                    "segments.product_category_level4": "Android",
                    "segments.product_category_level5": "Samsung",
                    "segments.product_channel": "UNSPECIFIED",
                    "segments.product_channel_exclusivity": "SINGLE_CHANNEL",
                    "segments.click_type": "APP_DEEPLINK",
                    "metrics.clicks": 10,
                    "metrics.conversions_from_interactions_rate": 0.5,
                    "metrics.conversions_value": 100.5,
                    "metrics.conversions": 4.0,
                    "metrics.cost_micros": 5000000,
                    "metrics.cost_per_all_conversions": 25.05,
                    "metrics.cost_per_conversion": 6.25,
                    "segments.product_country": "US",
                    "metrics.cross_device_conversions": 2.0,
                    "metrics.ctr": 0.1,
                    "segments.product_custom_attribute0": "Attribute 0",
                    "segments.product_custom_attribute1": "Attribute 1",
                    "segments.product_custom_attribute2": "Attribute 2",
                    "segments.product_custom_attribute3": "Attribute 3",
                    "segments.product_custom_attribute4": "Attribute 4",
                    "segments.date": "2023-11-22",
                    "segments.day_of_week": "FRIDAY",
                    "segments.device": "TABLET",
                    "customer.id": 123,
                    "metrics.impressions": 100,
                    "segments.product_language": "English",
                    "segments.product_merchant_id": 54321,
                    "segments.month": "November",
                    "segments.product_item_id": "ITEM123",
                    "segments.product_condition": 2,
                    "segments.product_title": "Samsung Galaxy S23",
                    "segments.product_type_l1": "Electronics",
                    "segments.product_type_l2": "Phones",
                    "segments.product_type_l3": "Smartphones",
                    "segments.product_type_l4": "Android",
                    "segments.product_type_l5": "Samsung",
                    "segments.quarter": "Q4",
                    "segments.product_store_id": "STORE123",
                    "metrics.value_per_all_conversions": 30.05,
                    "metrics.value_per_conversion": 7.5,
                    "segments.week": "38",
                    "segments.year": 2023,
                },
            ],
        ),
    ],
)
def test_empty_streams(mocker, stream_fixture_name, expected_records, request):
    """
    A test with synthetic data since we are not able to test `annotations_stream` and `cohorts_stream` streams
    due to free subscription plan for the sandbox
    """
    stream = request.getfixturevalue(stream_fixture_name)
    send_request_result = [create_google_ads_row_from_dict(expected_record) for expected_record in expected_records]
    mocker.patch("source_google_ads.google_ads.GoogleAds.send_request", return_value=[send_request_result])

    records_reader = stream.read_records(
        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice={"customer_id": "123", "login_customer_id": "123"}
    )
    assert list(records_reader) == expected_records
