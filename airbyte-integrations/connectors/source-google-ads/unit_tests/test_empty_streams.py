# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import patch

from source_google_ads.source import SourceGoogleAds

from .conftest import find_stream, read_full_refresh


@patch.object(SourceGoogleAds, "get_customers", return_value=[])
def test_query_shopping_performance_view_stream(customers, config, requests_mock):
    config["end_date"] = "2021-01-10"
    config["conversion_window_days"] = 3
    config["credentials"]["access_token"] = "access_token"
    stream = find_stream("shopping_performance_view", config)

    # Mocked responses
    access_token_response = [{"json": {"access_token": "access_token"}, "status_code": 200}]

    accessible_customers_response = [
        {
            "json": {"resourceNames": ["customers/1234567890"]},
            "status_code": 200,
        }
    ]

    customers_response = [
        {
            "json": {
                "results": [
                    {
                        "customerClient": {
                            "clientCustomer": "customers/123",
                            "manager": False,
                            "status": "ENABLED",
                            "id": "123",
                        }
                    }
                ]
            },
            "status_code": 200,
        }
    ]

    shopping_performance_view_response = [
        {
            "json": {
                "results": [
                    {
                        "AdGroup": {"id": 1, "name": "Test Ad Group", "status": "ENABLED"},
                        "Customer": {"descriptiveName": "Test Customer", "id": 1234567890},
                        "Campaign": {"id": 1234, "name": "Test Campaign", "status": "ENABLED"},
                        "Segments": {"date": "2021-01-08", "adNetworkType": "SEARCH"},
                        "Metrics": {"clicks": 25, "ctr": 0.5, "impressions": 500},
                    }
                ]
            },
            "status_code": 200,
        }
    ]

    # Register mocks
    requests_mock.register_uri("POST", "https://www.googleapis.com/oauth2/v3/token", access_token_response)
    requests_mock.register_uri(
        "GET", "https://googleads.googleapis.com/v20/customers:listAccessibleCustomers", accessible_customers_response
    )
    requests_mock.register_uri(
        "POST", "https://googleads.googleapis.com/v20/customers/1234567890/googleAds:searchStream", customers_response
    )

    request_history = requests_mock.register_uri(
        "POST",
        "https://googleads.googleapis.com/v20/customers/123/googleAds:search",
        shopping_performance_view_response,
    )

    # Run sync
    records = read_full_refresh(stream_instance=stream)
    assert len(records) == 1
    record = records[0]

    # This is what the record should look like AFTER flattening & snake_case transforms
    expected_record = {
        "ad_group.id": 1,
        "ad_group.name": "Test Ad Group",
        "ad_group.status": "ENABLED",
        "customer.descriptive_name": "Test Customer",
        "customer.id": 1234567890,
        "campaign.id": 1234,
        "campaign.name": "Test Campaign",
        "campaign.status": "ENABLED",
        "segments.date": "2021-01-08",
        "segments.ad_network_type": "SEARCH",
        "metrics.clicks": 25,
        "metrics.ctr": 0.5,
        "metrics.impressions": 500,
    }

    # Assert the entire record
    assert json.dumps(record.data, sort_keys=True) == json.dumps(expected_record, sort_keys=True)

    # Verify the GAQL query
    request_json = json.loads(request_history.last_request.text)
    expected_query = "SELECT customer.descriptive_name, ad_group.id, ad_group.name, ad_group.status, segments.ad_network_type, segments.product_aggregator_id, metrics.all_conversions_from_interactions_rate, metrics.all_conversions_value, metrics.all_conversions, metrics.average_cpc, segments.product_brand, campaign.id, campaign.name, campaign.status, segments.product_category_level1, segments.product_category_level2, segments.product_category_level3, segments.product_category_level4, segments.product_category_level5, segments.product_channel, segments.product_channel_exclusivity, segments.click_type, metrics.clicks, metrics.conversions_from_interactions_rate, metrics.conversions_value, metrics.conversions, metrics.cost_micros, metrics.cost_per_all_conversions, metrics.cost_per_conversion, segments.product_country, metrics.cross_device_conversions, metrics.ctr, segments.product_custom_attribute0, segments.product_custom_attribute1, segments.product_custom_attribute2, segments.product_custom_attribute3, segments.product_custom_attribute4, segments.date, segments.day_of_week, segments.device, customer.id, metrics.impressions, segments.product_language, segments.product_merchant_id, segments.month, segments.product_item_id, segments.product_condition, segments.product_title, segments.product_type_l1, segments.product_type_l2, segments.product_type_l3, segments.product_type_l4, segments.product_type_l5, segments.quarter, segments.product_store_id, metrics.value_per_all_conversions, metrics.value_per_conversion, segments.week, segments.year FROM shopping_performance_view WHERE segments.date BETWEEN '2021-01-01' AND '2021-01-10' ORDER BY segments.date ASC"
    assert request_json["query"] == expected_query
