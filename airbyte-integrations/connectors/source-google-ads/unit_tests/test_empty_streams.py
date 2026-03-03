# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import re
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time

from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import Obj, find_stream, get_source, read_full_refresh


def test_query_shopping_performance_view_stream(customers, config, requests_mock):
    """
    Test that shopping_performance_view stream correctly processes and transforms data.

    Verifies:
    - OAuth token refresh
    - Customer account fetching
    - GAQL query generation with date filtering
    - Record transformation (PascalCase -> snake_case, flattening)
    """
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
                            "id": "1234567890",  # WARNING: this value needs to match the value in the config
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
        "https://googleads.googleapis.com/v20/customers/123/googleAds:searchStream",
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


def test_custom_query_stream(customers, config_for_custom_query_tests, requests_mock, mocker):
    """
    Test that custom query streams correctly generate schemas and execute queries.

    Verifies:
    - CustomGAQuerySchemaLoader dynamically generates JSON schema from Google Ads API metadata
    - Enum types are properly handled with all possible values
    - Date fields get the correct "format": "date" annotation
    - Incremental queries are properly transformed with date range filters
    - Record transformation matches expectations
    """
    config_for_custom_query_tests["end_date"] = "2021-01-10"
    config_for_custom_query_tests["conversion_window_days"] = 1
    config_for_custom_query_tests["credentials"]["access_token"] = "access_token"
    streams = get_source(config=config_for_custom_query_tests).streams(config=config_for_custom_query_tests)
    stream = next(filter(lambda s: s.name == "custom_ga_query", streams))

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

    custom_query_response = [
        {
            "json": {
                "results": [
                    {
                        "segments": {
                            "date": "2021-01-08",
                        },
                        "campaign_budget": {
                            "name": "Test Campaign Budget",
                        },
                        "campaign": {
                            "name": "Test Campaign",
                        },
                        "metrics": {
                            "interaction_event_types": ["ENGAGEMENT"],
                        },
                    }
                ]
            },
            "status_code": 200,
        }
    ]

    # Register mocks
    requests_mock.register_uri("POST", "https://www.googleapis.com/oauth2/v3/token", access_token_response)

    query_object = MagicMock(
        return_value={
            "campaign_budget.name": Obj(data_type=Obj(name="STRING"), is_repeated=False),
            "campaign.name": Obj(data_type=Obj(name="STRING"), is_repeated=False),
            "metrics.interaction_event_types": Obj(
                data_type=Obj(name="ENUM"),
                is_repeated=True,
                enum_values=["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"],
            ),
            "segments.date": Obj(data_type=Obj(name="DATE"), is_repeated=False),
        }
    )
    mocker.patch(
        "source_google_ads.components.CustomGAQuerySchemaLoader.google_ads_client", return_value=Obj(get_fields_metadata=query_object)
    )

    assert stream.get_json_schema() == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "campaign_budget.name": {"type": ["string", "null"]},
            "campaign.name": {"type": ["string", "null"]},
            "metrics.interaction_event_types": {
                "type": ["null", "array"],
                "items": {"type": "string", "enum": ["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"]},
            },
            "segments.date": {"type": ["string", "null"], "format": "date"},
        },
        "additionalProperties": True,
    }

    requests_mock.register_uri(
        "GET", "https://googleads.googleapis.com/v20/customers:listAccessibleCustomers", accessible_customers_response
    )
    requests_mock.register_uri(
        "POST", "https://googleads.googleapis.com/v20/customers/1234567890/googleAds:searchStream", customers_response
    )

    request_history = requests_mock.register_uri(
        "POST",
        "https://googleads.googleapis.com/v20/customers/123/googleAds:searchStream",
        custom_query_response,
    )

    # Run sync
    records = read_full_refresh(stream_instance=stream)
    assert len(records) == 1
    record = records[0]

    # This is what the record should look like AFTER flattening & snake_case transforms
    expected_record = {
        "campaign_budget.name": "Test Campaign Budget",
        "campaign.name": "Test Campaign",
        "metrics.interaction_event_types": ["3"],
        "segments.date": "2021-01-08",
    }

    # Assert the entire record
    assert json.dumps(record.data, sort_keys=True) == json.dumps(expected_record, sort_keys=True)

    # Verify the GAQL query
    request_json = json.loads(request_history.last_request.text)
    expected_query = "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types, segments.date FROM campaign_budget WHERE segments.date BETWEEN '2021-01-01' AND '2021-01-10' ORDER BY segments.date ASC"
    assert request_json["query"] == expected_query


@pytest.mark.parametrize(
    "query, expected_incremental_sync",
    [
        ("\tselect\rad.id,\tsegments.date,\tad.resource_name\nfrom\nad", True),
        ("\nselect ad.id, segments.date from ad", True),
        ("select ad.id, segments.date\nfrom\nad\norder\n  by segments.date", True),
        ("\nselect\nad.id,\nsegments.date\nfrom\nad\norder\n  by segments.date", True),
        ("SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget", False),
        (
            "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget ORDER BY campaign_budget.name DESC",
            False,
        ),
        ("SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad", True),
        ("SELECT \n ad_group_ad.ad.name, \n segments.date FROM ad_group_ad ORDER BY \n segments.date DESC", True),
        ("SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad ORDER BY segments.date DESC", True),
        ("SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad ORDER BY ad_group_ad.ad.name, segments.date DESC", True),
        ("SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad ORDER BY segments.date DESC LIMIT 100", True),
        (
            "SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad ORDER BY ad_group_ad.ad.name DESC, segments.date DESC LIMIT 100",
            True,
        ),
        (
            "SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad ORDER BY segments.date DESC, ad_group_ad.ad.name DESC LIMIT 100",
            True,
        ),
        ("SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad WHERE segments.date DURING LAST_30_DAYS", False),
        ("SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad WHERE \n segments.date DURING LAST_30_DAYS", False),
        (
            "SELECT ad_group_ad.ad.name, segments.date FROM ad_group_ad WHERE segments.date DURING LAST_30_DAYS ORDER BY ad_group_ad.ad.name",
            False,
        ),
        # Click view queries - incremental detection only (step override tested in test_custom_query_click_view_retention_and_step)
        ("SELECT click_view.gclid, segments.date FROM click_view", True),
        ("select click_view.gclid, segments.date from click_view", True),
        ("SELECT click_view.gclid, segments.date FROM click_view ORDER BY segments.date", True),
        ("SELECT click_view.gclid, segments.date FROM click_view ORDER BY segments.date ASC", True),
        (
            """SELECT
                click_view.gclid,
                segments.date
            FROM
                click_view""",
            True,
        ),
        (
            "SELECT click_view.gclid, click_view.ad_group_ad, segments.date FROM click_view WHERE segments.date BETWEEN '2025-10-21' AND '2025-10-21'",
            False,
        ),
    ],
)
def test_custom_query_stream_with_different_queries(query, expected_incremental_sync, config_for_custom_query_tests):
    """
    Test that the manifest regex correctly identifies incremental queries and assigns correct requester class.

    Verifies that queries with segments.date are correctly detected by the ComponentMappingDefinition
    regex patterns and configured as incremental streams. The condition matches:
    - 1 segments.date with SELECT...FROM pattern, OR
    - 2 segments.date with SELECT...FROM AND ORDER BY patterns

    Also verifies that incremental click_view queries use CustomGAQueryClickViewHttpRequester.

    Note: Step override behavior is tested in test_custom_query_click_view_retention_and_step.
    """
    config = config_for_custom_query_tests
    config["custom_queries_array"][0]["query"] = query

    streams = get_source(config=config).streams(config=config)
    stream = next(filter(lambda s: s.name == "custom_ga_query", streams))

    # Verify that the regex matching correctly identifies incremental vs full-refresh queries
    if expected_incremental_sync:
        assert stream.cursor_field == "segments.date", f"Stream cursor field should be 'segments.date' for query: {query}"
    else:
        assert stream.cursor_field != "segments.date", f"Stream should not have segments.date as cursor field for query: {query}"

    # Check if this is a click_view query using regex (case-insensitive)
    # Matches patterns like: "FROM click_view", "from CLICK_VIEW", etc.
    is_click_view = bool(re.search(r"\bFROM\s+click_view\b", query, re.IGNORECASE))

    # Verify the requester class for incremental queries
    # Access chain: stream -> partition_generator -> partition_factory -> retriever -> requester
    # This retrieves the HTTP requester instance to verify its class type
    requester_class_name = stream._stream_partition_generator._partition_factory._retriever.requester.__class__.__name__
    if expected_incremental_sync and is_click_view:
        assert requester_class_name == "CustomGAQueryClickViewHttpRequester", (
            f"Click view incremental queries should use CustomGAQueryClickViewHttpRequester.\n"
            f"Query: {query}\n"
            f"Actual requester class: {requester_class_name}"
        )
    else:
        assert requester_class_name == "CustomGAQueryHttpRequester", (
            f"Regular queries should use CustomGAQueryHttpRequester.\n"
            f"Query: {query}\n"
            f"Actual requester class: {requester_class_name}"
        )


@pytest.mark.parametrize(
    "query, has_metrics",
    [
        ("SELECT campaign.id, metrics.clicks, segments.date FROM campaign", True),
        ("SELECT ad_group.name, metrics.impressions, segments.date FROM ad_group", True),
        ("SELECT campaign.name, metrics.cost_micros FROM campaign", True),
        ("SELECT campaign.id, campaign.name, segments.date FROM campaign", False),
        ("SELECT ad_group.id, segments.date FROM ad_group", False),
    ],
    ids=["metrics_clicks", "metrics_impressions", "metrics_cost", "no_metrics_1", "no_metrics_2"],
)
def test_custom_query_partition_router_for_metrics(query, has_metrics, config_for_custom_query_tests):
    """
    Test that partition router is correctly added for queries with metrics.

    Verifies that the ComponentMappingDefinition in manifest correctly
    adds the customer_client_non_manager partition router when the query contains 'metrics'.
    """
    config = config_for_custom_query_tests.copy()
    stream_name = "test_partition"
    config["custom_queries_array"] = [
        {
            "query": query,
            "table_name": stream_name,
        }
    ]

    streams = get_source(config=config).streams(config=config)
    stream = next(filter(lambda s: s.name == stream_name, streams))

    # Navigate through the stream's partition routing structure to get the parent stream query
    # When metrics are present, the ComponentMappingDefinition adds a partition router with
    # customer_client_non_manager as the parent stream, which filters to non-manager accounts
    stream_slicer = stream._stream_partition_generator._stream_slicer
    partition_router = stream_slicer._partition_router if hasattr(stream_slicer, "_partition_router") else stream_slicer
    parent_stream = partition_router.parent_stream_configs[0].stream
    parent_stream_requester = parent_stream._stream_partition_generator._partition_factory._retriever.requester
    parent_query = parent_stream_requester.request_options_provider.request_body_json["query"]

    # Verify the parent stream query differs based on whether metrics are present
    # Metrics queries need customer partitioning (manager = FALSE filter)
    if has_metrics:
        assert (
            parent_query
            == "SELECT customer_client.client_customer, customer_client.level, customer_client.id, customer_client.manager, customer_client.time_zone, customer_client.status FROM customer_client WHERE customer_client.manager = FALSE"
        )
    else:
        assert (
            parent_query
            == "SELECT\n  customer_client.client_customer,\n  customer_client.level,\n  customer_client.id,\n  customer_client.manager,\n  customer_client.time_zone,\n  customer_client.status\nFROM\n  customer_client\n"
        )


@pytest.mark.parametrize(
    "query, is_click_view",
    [
        # Click view queries should have 90-day retention and P1D step
        ("SELECT click_view.gclid, segments.date FROM click_view", True),
        ("SELECT\tclick_view.gclid,\tsegments.date\tFROM\tclick_view\tORDER\tBY\tsegments.date", True),
        ("select click_view.ad_group_ad, segments.date from click_view", True),
        # Regular queries should use config.start_date and P14D step
        ("SELECT ad_group.id, segments.date FROM ad_group", False),
        ("SELECT campaign.name, segments.date FROM campaign ORDER BY segments.date", False),
    ],
)
@pytest.mark.parametrize(
    "state_date, expected_start_click_view, expected_start_regular",
    [
        # No state - use retention dates
        # click_view: 2025-01-01 minus 90 days = 2024-10-03
        # regular: config.start_date = 2023-06-01
        (None, "2024-10-03", "2023-06-01"),
        # State within retention - use state date
        # Both use state date since it's within the allowed range
        ("2024-12-01", "2024-12-01", "2024-12-01"),
        # State before retention - click_view enforces retention, regular uses state
        # click_view: Ignores old state, uses 2024-10-03 (90-day limit)
        # regular: Uses state date 2024-01-01
        ("2024-01-01", "2024-10-03", "2024-01-01"),
    ],
    ids=["no_state", "state_within_retention", "state_before_retention"],
)
@freeze_time("2025-01-01")
def test_custom_query_click_view_retention_and_step(
    query, is_click_view, state_date, expected_start_click_view, expected_start_regular, config_for_custom_query_tests
):
    """
    Test that click_view custom queries have correct step override and retention.

    This test freezes time to 2025-01-01 and verifies:
    - click_view queries: P1D step (1 day) - verifies step override in manifest (lines 1033-1053)
    - click_view queries: 90-day retention via start_datetime override in manifest (lines 1054-1079)
    - regular queries: P14D step (14 days) - default for incremental queries
    - regular queries: use config.start_date for retention

    Tests three state scenarios:
    1. No state - uses retention dates
    2. State within retention - uses state date
    3. State before retention - click_view enforces retention, regular uses state
    """
    config = config_for_custom_query_tests.copy()
    config["start_date"] = "2023-06-01"
    stream_name = "test_query"
    config["custom_queries_array"] = [
        {
            "query": query,
            "table_name": stream_name,
        }
    ]

    # Create source with or without state
    if state_date:
        state = StateBuilder().with_stream_state(stream_name, {"state": {"segments.date": state_date}}).build()
        streams = get_source(config=config, state=state).streams(config=config)
    else:
        streams = get_source(config=config).streams(config=config)

    stream = next(filter(lambda s: s.name == stream_name, streams))

    # Verify incremental sync is enabled (all these queries have segments.date)
    assert stream.cursor_field == "segments.date", f"Stream cursor field should be 'segments.date' for: {query}"

    # Verify step override (P1D for click_view, P14D for regular)
    cursor = stream.cursor._create_cursor(stream.cursor._global_cursor)
    actual_step_days = cursor._slice_range.days
    expected_step_days = 1 if is_click_view else 14

    assert actual_step_days == expected_step_days, (
        f"Step days mismatch.\n"
        f"Query: {query}\n"
        f"State: {state_date}\n"
        f"Expected: {expected_step_days} days\n"
        f"Actual: {actual_step_days} days"
    )

    # Verify start date (retention behavior)
    expected_start_date = expected_start_click_view if is_click_view else expected_start_regular
    actual_start_date = cursor.state["segments.date"]

    assert actual_start_date == expected_start_date, (
        f"Start date mismatch.\n"
        f"Query: {query}\n"
        f"State: {state_date}\n"
        f"Expected start date: {expected_start_date}\n"
        f"Actual start date: {actual_start_date}\n"
        f"Click view should enforce 90-day retention (2024-10-03), regular queries use config.start_date or state."
    )
