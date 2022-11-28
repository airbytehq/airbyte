#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

from source_dv_360.streams import DBM


def test_convert_fields():
    fields = ["app_url_id", "cm_placement_id", "pct_clicks_leading_to_conversions", "region_id", "date"]
    converted_fields = DBM.convert_fields(fields)
    expected_fields = [
        "FILTER_SITE_ID",
        "FILTER_CM_PLACEMENT_ID",
        "METRIC_CLICK_TO_POST_CLICK_CONVERSION_RATE",
        "FILTER_REGION",
        "FILTER_DATE",
    ]

    assert converted_fields == expected_fields


with open("source_dv_360/schemas/reach.json") as FILE:
    SCHEMA = json.loads(FILE.read())

CATALOG_FIELDS = [
    "advertiser",
    "advertiser_id",
    "advertiser_integration_code",
    "advertiser_status",
    "app_url",
    "campaign",
    "campaign_id",
    "creative",
    "creative_id",
    "creative_source",
    "date",
    "insertion_order",
    "insertion_order_id",
    "insertion_order_integration_code",
    "insertion_order_status",
    "inventory_source",
    "line_item",
    "line_item_id",
    "line_item_status",
    "partner",
    "partner_id",
    "partner_status",
    "targeted_data_providers",
    "cookie_reach_average_impression_frequency",
    "cookie_reach_impression_reach",
    "unique_reach_average_impression_frequency",
    "unique_reach_click_reach",
    "unique_reach_impression_reach",
]


def test_get_fields_from_schema():
    fields = DBM.get_fields_from_schema(SCHEMA, CATALOG_FIELDS)
    expected_fields = [
        "advertiser",
        "advertiser_id",
        "advertiser_integration_code",
        "advertiser_status",
        "app_url",
        "campaign",
        "campaign_id",
        "creative",
        "creative_id",
        "creative_source",
        "date",
        "insertion_order",
        "insertion_order_id",
        "insertion_order_integration_code",
        "insertion_order_status",
        "inventory_source",
        "line_item",
        "line_item_id",
        "line_item_status",
        "partner",
        "partner_id",
        "partner_status",
        "targeted_data_providers",
        "cookie_reach_average_impression_frequency",
        "cookie_reach_impression_reach",
        "unique_reach_average_impression_frequency",
        "unique_reach_click_reach",
        "unique_reach_impression_reach",
    ]
    assert expected_fields == fields


def test_get_dimensions_from_fields():
    fields = DBM.get_fields_from_schema(SCHEMA, CATALOG_FIELDS)
    diemsions = DBM.get_dimensions_from_fields(fields)
    expected_diemsions = [
        "FILTER_ADVERTISER_NAME",
        "FILTER_ADVERTISER",
        "FILTER_ADVERTISER_INTEGRATION_CODE",
        "FILTER_ADVERTISER_INTEGRATION_STATUS",
        "FILTER_APP_URL",
        "FILTER_MEDIA_PLAN_NAME",
        "FILTER_MEDIA_PLAN",
        "FILTER_CREATIVE",
        "FILTER_CREATIVE_ID",
        "FILTER_CREATIVE_SOURCE",
        "FILTER_DATE",
        "FILTER_INSERTION_ORDER_NAME",
        "FILTER_INSERTION_ORDER",
        "FILTER_INSERTION_ORDER_INTEGRATION_CODE",
        "FILTER_INSERTION_ORDER_STATUS",
        "FILTER_INVENTORY_SOURCE_NAME",
        "FILTER_LINE_ITEM_NAME",
        "FILTER_LINE_ITEM",
        "FILTER_LINE_ITEM_STATUS",
        "FILTER_PARTNER_NAME",
        "FILTER_PARTNER",
        "FILTER_PARTNER_STATUS",
        "FILTER_TARGETED_DATA_PROVIDERS",
    ]
    assert expected_diemsions == diemsions


def test_get_metrics_from_fields():
    fields = DBM.get_fields_from_schema(SCHEMA, CATALOG_FIELDS)
    metrics = DBM.get_metrics_from_fields(fields)
    expected_metrics = [
        "METRIC_COOKIE_REACH_AVERAGE_IMPRESSION_FREQUENCY",
        "METRIC_COOKIE_REACH_IMPRESSION_REACH",
        "METRIC_UNIQUE_REACH_AVERAGE_IMPRESSION_FREQUENCY",
        "METRIC_UNIQUE_REACH_CLICK_REACH",
        "METRIC_UNIQUE_REACH_IMPRESSION_REACH",
    ]
    assert expected_metrics == metrics


EXPECTED_QUERY = {
    "kind": "doubleclickbidmanager#query",
    "queryId": "0",
    "metadata": {
        "title": "reach",
        "dataRange": "CUSTOM_DATES",
        "format": "CSV",
        "running": False,
        "googleCloudStoragePathForLatestReport": "",
        "latestReportRunTimeMs": "0",
        "sendNotification": False,
    },
    "params": {
        "type": "TYPE_REACH_AND_FREQUENCY",
        "groupBys": [
            "FILTER_ADVERTISER_NAME",
            "FILTER_ADVERTISER",
            "FILTER_ADVERTISER_INTEGRATION_CODE",
            "FILTER_ADVERTISER_INTEGRATION_STATUS",
            "FILTER_APP_URL",
            "FILTER_MEDIA_PLAN_NAME",
            "FILTER_MEDIA_PLAN",
            "FILTER_CREATIVE",
            "FILTER_CREATIVE_ID",
            "FILTER_CREATIVE_SOURCE",
            "FILTER_DATE",
            "FILTER_INSERTION_ORDER_NAME",
            "FILTER_INSERTION_ORDER",
            "FILTER_INSERTION_ORDER_INTEGRATION_CODE",
            "FILTER_INSERTION_ORDER_STATUS",
            "FILTER_INVENTORY_SOURCE_NAME",
            "FILTER_LINE_ITEM_NAME",
            "FILTER_LINE_ITEM",
            "FILTER_LINE_ITEM_STATUS",
            "FILTER_PARTNER_NAME",
            "FILTER_PARTNER",
            "FILTER_PARTNER_STATUS",
            "FILTER_TARGETED_DATA_PROVIDERS",
        ],
        "filters": [{"type": "FILTER_PARTNER", "value": "123"}, {"type": "FILTER_LINE_ITEM", "value": 55}],
        "metrics": [
            "METRIC_COOKIE_REACH_AVERAGE_IMPRESSION_FREQUENCY",
            "METRIC_COOKIE_REACH_IMPRESSION_REACH",
            "METRIC_UNIQUE_REACH_AVERAGE_IMPRESSION_FREQUENCY",
            "METRIC_UNIQUE_REACH_CLICK_REACH",
            "METRIC_UNIQUE_REACH_IMPRESSION_REACH",
        ],
        "options": {"includeOnlyTargetedUserLists": False},
    },
    "schedule": {"frequency": "ONE_TIME"},
    "reportDataStartTimeMs": "1646092800000",
    "reportDataEndTimeMs": "1646697600000",
    "timezoneCode": "UTC",
}


def test_create_query_object():
    query = DBM.create_query_object(
        report_name="reach",
        dimensions=[
            "FILTER_ADVERTISER_NAME",
            "FILTER_ADVERTISER",
            "FILTER_ADVERTISER_INTEGRATION_CODE",
            "FILTER_ADVERTISER_INTEGRATION_STATUS",
            "FILTER_APP_URL",
            "FILTER_MEDIA_PLAN_NAME",
            "FILTER_MEDIA_PLAN",
            "FILTER_CREATIVE",
            "FILTER_CREATIVE_ID",
            "FILTER_CREATIVE_SOURCE",
            "FILTER_DATE",
            "FILTER_INSERTION_ORDER_NAME",
            "FILTER_INSERTION_ORDER",
            "FILTER_INSERTION_ORDER_INTEGRATION_CODE",
            "FILTER_INSERTION_ORDER_STATUS",
            "FILTER_INVENTORY_SOURCE_NAME",
            "FILTER_LINE_ITEM_NAME",
            "FILTER_LINE_ITEM",
            "FILTER_LINE_ITEM_STATUS",
            "FILTER_PARTNER_NAME",
            "FILTER_PARTNER",
            "FILTER_PARTNER_STATUS",
            "FILTER_TARGETED_DATA_PROVIDERS",
        ],
        metrics=[
            "METRIC_COOKIE_REACH_AVERAGE_IMPRESSION_FREQUENCY",
            "METRIC_COOKIE_REACH_IMPRESSION_REACH",
            "METRIC_UNIQUE_REACH_AVERAGE_IMPRESSION_FREQUENCY",
            "METRIC_UNIQUE_REACH_CLICK_REACH",
            "METRIC_UNIQUE_REACH_IMPRESSION_REACH",
        ],
        start_date="2022-03-01",
        end_date="2022-03-08",
        partner_id="123",
        filters=[{"type": "FILTER_LINE_ITEM", "value": 55}],
    )
    assert query == EXPECTED_QUERY
