#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import pytest
from airbyte_cdk.models import SyncMode
from google.ads.googleads.v15.services.types.google_ads_service import GoogleAdsRow
from source_google_ads.source import SourceGoogleAds


@pytest.fixture(scope="module")
def config():
    with open(Path(__file__).parent.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())


@pytest.fixture(scope="module")
def streams(config):
    return SourceGoogleAds().streams(config=config)


@pytest.fixture(scope="module")
def account_labels(streams):
    return next(filter(lambda s: s.name == "account_labels", streams))


@pytest.fixture(scope="module")
def shopping_performance_report(streams):
    return next(filter(lambda s: s.name == "shopping_performance_report", streams))


def create_google_ads_row_from_dict(data: dict) -> GoogleAdsRow:
    row = GoogleAdsRow()

    for key, value in data.items():
        # Split the key to check for nested fields
        parts = key.split(".")

        # Handle nested fields
        if len(parts) > 1:
            parent_field = parts[0]
            nested_field = parts[1]

            # Check if the parent field exists and create if not
            if not hasattr(row, parent_field):
                setattr(
                    row, parent_field, row.__class__()
                )  # Assuming the nested message type is the same as the parent. Adjust if different.

            # Set the nested field value
            nested_obj = getattr(row, parent_field)
            setattr(nested_obj, nested_field, value)
        else:
            # Handle non-nested fields
            if hasattr(row, key):
                setattr(row, key, value)
            else:
                print(f"Warning: Unknown field '{key}' for GoogleAdsRow")

    return row


@pytest.mark.parametrize(
    "stream_fixture_name, expected_records",
    [
        (
            "account_labels",
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
            "shopping_performance_report",
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
    records_reader = stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice={"customer_id": "123"})
    send_request_result = [create_google_ads_row_from_dict(expected_record) for expected_record in expected_records]
    mocker.patch("source_google_ads.google_ads.GoogleAds.send_request", return_value=[send_request_result])

    assert list(records_reader) == expected_records
