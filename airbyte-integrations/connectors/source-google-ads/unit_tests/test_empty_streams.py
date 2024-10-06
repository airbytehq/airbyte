# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import CustomerLabel, ShoppingPerformanceView


def test_query_customer_label_stream(customers, config):
    credentials = config["credentials"]
    api = GoogleAds(credentials=credentials)

    stream_config = dict(
        api=api,
        customers=customers,
    )
    stream = CustomerLabel(**stream_config)
    assert (
        stream.get_query(stream_slice={"customer_id": "123"})
        == "SELECT customer_label.resource_name, customer_label.customer, customer.id, customer_label.label FROM customer_label"
    )


def test_query_shopping_performance_view_stream(customers, config):
    credentials = config["credentials"]
    api = GoogleAds(credentials=credentials)

    stream_config = dict(
        api=api,
        start_date="2023-01-01 00:00:00.000000",
        conversion_window_days=0,
        customers=customers,
    )
    stream = ShoppingPerformanceView(**stream_config)
    stream_slice = {
        "start_date": "2023-01-01 00:00:00.000000",
        "end_date": "2023-09-19 00:00:00.000000",
        "resource_type": "SOME_RESOURCE_TYPE",
        "login_customer_id": "default",
    }
    expected_query = "SELECT customer.descriptive_name, ad_group.id, ad_group.name, ad_group.status, segments.ad_network_type, segments.product_aggregator_id, metrics.all_conversions_from_interactions_rate, metrics.all_conversions_value, metrics.all_conversions, metrics.average_cpc, segments.product_brand, campaign.id, campaign.name, campaign.status, segments.product_category_level1, segments.product_category_level2, segments.product_category_level3, segments.product_category_level4, segments.product_category_level5, segments.product_channel, segments.product_channel_exclusivity, segments.click_type, metrics.clicks, metrics.conversions_from_interactions_rate, metrics.conversions_value, metrics.conversions, metrics.cost_micros, metrics.cost_per_all_conversions, metrics.cost_per_conversion, segments.product_country, metrics.cross_device_conversions, metrics.ctr, segments.product_custom_attribute0, segments.product_custom_attribute1, segments.product_custom_attribute2, segments.product_custom_attribute3, segments.product_custom_attribute4, segments.date, segments.day_of_week, segments.device, customer.id, metrics.impressions, segments.product_language, segments.product_merchant_id, segments.month, segments.product_item_id, segments.product_condition, segments.product_title, segments.product_type_l1, segments.product_type_l2, segments.product_type_l3, segments.product_type_l4, segments.product_type_l5, segments.quarter, segments.product_store_id, metrics.value_per_all_conversions, metrics.value_per_conversion, segments.week, segments.year FROM shopping_performance_view WHERE segments.date >= '2023-01-01 00:00:00.000000' AND segments.date <= '2023-09-19 00:00:00.000000' ORDER BY segments.date ASC"
    assert stream.get_query(stream_slice=stream_slice) == expected_query
