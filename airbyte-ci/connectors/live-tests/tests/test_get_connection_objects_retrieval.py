# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import uuid
from unittest.mock import patch
from uuid import UUID

from connection_retriever import ConnectionObject
from connection_retriever.retrieval import TestingCandidate
from connection_retriever.utils import ConnectionSubset

from live_tests.commons.connection_objects_retrieval import _get_connection_objects_from_retrieved_objects

mocking_return_of_retrieve_testing_candidates = [
    TestingCandidate(
        connection_id="0b11bcb3-7726-4d1a-bcb4-d68fb579f7a8",
        connection_url=f"https://cloud.airbyte.com/workspaces/{str(uuid.uuid4())}/connections/{str(uuid.uuid4())}",
        catalog=None,
        configured_catalog=None,
        state=None,
        workspace_id=None,
        destination_docker_image=None,
        source_docker_image=None,
        last_attempt_duration_in_microseconds=44902474342,
        streams_with_data=[
            "sponsored_products_report_stream",
            "profiles",
            "sponsored_display_report_stream",
            "sponsored_brands_v3_report_stream",
        ],
    ),
    TestingCandidate(
        connection_id="8775fd75-e510-4f7f-98dc-0128ea997133",
        connection_url=f"https://cloud.airbyte.com/workspaces/{str(uuid.uuid4())}/connections/{str(uuid.uuid4())}",
        catalog=None,
        configured_catalog=None,
        state=None,
        workspace_id=None,
        destination_docker_image=None,
        source_docker_image=None,
        last_attempt_duration_in_microseconds=44902474342,
        streams_with_data=[
            "sponsored_products_report_stream",
            "sponsored_display_report_stream",
            "profiles",
            "sponsored_brands_v3_report_stream",
        ],
    ),
]

mocking_return_of_retrieve_objects = [
    TestingCandidate(
        connection_id="0b11bcb3-7726-4d1a-bcb4-d68fb579f7a8",
        connection_url=f"https://cloud.airbyte.com/workspaces/{str(uuid.uuid4())}/connections/{str(uuid.uuid4())}",
        catalog={
            "streams": [
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "countryCode": {"type": [...]},
                        },
                        "title": "profiles",
                        "type": ["null", "object"],
                    },
                    "name": "profiles",
                    "source_defined_primary_key": [["profileId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "state": {"type": [...]},
                        },
                        "title": "portfolios",
                        "type": ["null", "object"],
                    },
                    "name": "portfolios",
                    "source_defined_primary_key": [["portfolioId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "tactic": {"type": [...]},
                        },
                        "title": "sponsored_display_campaigns",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_display_campaigns",
                    "source_defined_primary_key": [["campaignId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "tactic": {"type": [...]},
                        },
                        "title": "sponsored_display_ad_groups",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_display_ad_groups",
                    "source_defined_primary_key": [["adGroupId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "state": {"type": [...]},
                        },
                        "title": "sponsored_display_product_ads",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_display_product_ads",
                    "source_defined_primary_key": [["adId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "targetId": {"type": [...]},
                        },
                        "title": "sponsored_display_targetings",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_display_targetings",
                    "source_defined_primary_key": [["targetId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "properties": {"type": [...]},
                        },
                        "title": "sponsored_display_creatives",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_display_creatives",
                    "source_defined_primary_key": [["creativeId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "createdDate": {"type": [...]},
                        },
                        "title": "sponsored_display_budget_rules",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_display_budget_rules",
                    "source_defined_primary_key": [["ruleId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "sponsored_brands_keywords",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_brands_keywords",
                    "source_defined_primary_key": [["adGroupId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "bidding": {"type": [...]},
                        },
                        "title": "sponsored_brands_campaigns",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_brands_campaigns",
                    "source_defined_primary_key": [["campaignId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "sponsored_brands_ad_groups",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_brands_ad_groups",
                    "source_defined_primary_key": [["adGroupId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "budget": {"type": [...]},
                        },
                        "title": "sponsored_product_campaigns",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_campaigns",
                    "source_defined_primary_key": [["campaignId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "sponsored_product_ad_groups",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_ad_groups",
                    "source_defined_primary_key": [["adGroupId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "sponsored_product_keywords",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_keywords",
                    "source_defined_primary_key": [["keywordId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "sponsored_product_negative_keywords",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_negative_keywords",
                    "source_defined_primary_key": [["keywordId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "sponsored_product_campaign_negative_keywords",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_campaign_negative_keywords",
                    "source_defined_primary_key": [["keywordId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "sponsored_product_ads",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_ads",
                    "source_defined_primary_key": [["adId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "sponsored_product_targetings",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_targetings",
                    "source_defined_primary_key": [["targetId"]],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                            "bidRecommendationsForTargetingExpressions": {"items": {...}, "type": "array"},
                            "campaignId": {"type": [...]},
                            "theme": {"type": [...]},
                        },
                        "title": "sponsored_product_ad_group_bid_recommendations",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_ad_group_bid_recommendations",
                    "source_defined_primary_key": [],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {"adGroupId": {"type": [...]}, "suggestedKeywords": {"items": {...}, "type": [...]}},
                        "title": "sponsored_product_ad_group_suggested_keywords",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_product_ad_group_suggested_keywords",
                    "source_defined_primary_key": [],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "attribution_report_products",
                        "type": ["null", "object"],
                    },
                    "name": "attribution_report_products",
                    "source_defined_primary_key": [],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "attribution_report_performance_adgroup",
                        "type": ["null", "object"],
                    },
                    "name": "attribution_report_performance_adgroup",
                    "source_defined_primary_key": [],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "attribution_report_performance_campaign",
                        "type": ["null", "object"],
                    },
                    "name": "attribution_report_performance_campaign",
                    "source_defined_primary_key": [],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": [],
                    "is_resumable": False,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "adGroupId": {"type": [...]},
                        },
                        "title": "attribution_report_performance_creative",
                        "type": ["null", "object"],
                    },
                    "name": "attribution_report_performance_creative",
                    "source_defined_primary_key": [],
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "default_cursor_field": ["reportDate"],
                    "is_resumable": True,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "profileId": {"type": [...]},
                        },
                        "title": "sponsored_display_report_stream",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_display_report_stream",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
                {
                    "default_cursor_field": ["reportDate"],
                    "is_resumable": True,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "profileId": {"type": [...]},
                        },
                        "title": "sponsored_brands_v3_report_stream",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_brands_v3_report_stream",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
                {
                    "default_cursor_field": ["reportDate"],
                    "is_resumable": True,
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "properties": {
                            "profileId": {"type": [...]},
                        },
                        "title": "sponsored_products_report_stream",
                        "type": ["null", "object"],
                    },
                    "name": "sponsored_products_report_stream",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
            ]
        },
        configured_catalog={
            "streams": [
                {
                    "cursor_field": ["reportDate"],
                    "destination_sync_mode": "append_dedup",
                    "fields": [
                        {"name": "metric", "type": "OBJECT"},
                        {"name": "recordId", "type": "STRING"},
                        {"name": "profileId", "type": "INTEGER"},
                        {"name": "recordType", "type": "STRING"},
                        {"name": "reportDate", "type": "STRING"},
                    ],
                    "mappers": [],
                    "primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                    "stream": {
                        "default_cursor_field": ["reportDate"],
                        "is_resumable": False,
                        "json_schema": {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "properties": {
                                "metric": {...},
                                "profileId": {...},
                                "recordId": {...},
                                "recordType": {...},
                                "reportDate": {...},
                            },
                            "title": "sponsored_display_report_stream",
                            "type": ["null", "object"],
                        },
                        "name": "sponsored_display_report_stream",
                        "source_defined_cursor": True,
                        "source_defined_primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                        "supported_sync_modes": ["full_refresh", "incremental"],
                    },
                    "sync_mode": "incremental",
                },
                {
                    "cursor_field": [],
                    "destination_sync_mode": "overwrite_dedup",
                    "fields": [
                        {"name": "timezone", "type": "STRING"},
                        {"name": "profileId", "type": "INTEGER"},
                        {"name": "accountInfo", "type": "OBJECT"},
                        {"name": "countryCode", "type": "STRING"},
                        {"name": "dailyBudget", "type": "NUMBER"},
                        {"name": "currencyCode", "type": "STRING"},
                    ],
                    "mappers": [],
                    "primary_key": [["profileId"]],
                    "stream": {
                        "default_cursor_field": [],
                        "is_resumable": False,
                        "json_schema": {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "properties": {
                                "accountInfo": {...},
                                "countryCode": {...},
                                "currencyCode": {...},
                                "dailyBudget": {...},
                                "profileId": {...},
                                "timezone": {...},
                            },
                            "title": "profiles",
                            "type": ["null", "object"],
                        },
                        "name": "profiles",
                        "source_defined_cursor": False,
                        "source_defined_primary_key": [["profileId"]],
                        "supported_sync_modes": ["full_refresh"],
                    },
                    "sync_mode": "full_refresh",
                },
                {
                    "cursor_field": ["reportDate"],
                    "destination_sync_mode": "append_dedup",
                    "fields": [
                        {"name": "metric", "type": "OBJECT"},
                        {"name": "recordId", "type": "STRING"},
                        {"name": "profileId", "type": "INTEGER"},
                        {"name": "recordType", "type": "STRING"},
                        {"name": "reportDate", "type": "STRING"},
                    ],
                    "mappers": [],
                    "primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                    "stream": {
                        "default_cursor_field": ["reportDate"],
                        "is_resumable": False,
                        "json_schema": {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "properties": {
                                "metric": {...},
                                "profileId": {...},
                                "recordId": {...},
                                "recordType": {...},
                                "reportDate": {...},
                            },
                            "title": "sponsored_brands_v3_report_stream",
                            "type": ["null", "object"],
                        },
                        "name": "sponsored_brands_v3_report_stream",
                        "source_defined_cursor": True,
                        "source_defined_primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                        "supported_sync_modes": ["full_refresh", "incremental"],
                    },
                    "sync_mode": "incremental",
                },
                {
                    "cursor_field": ["reportDate"],
                    "destination_sync_mode": "append_dedup",
                    "fields": [
                        {"name": "metric", "type": "OBJECT"},
                        {"name": "recordId", "type": "STRING"},
                        {"name": "profileId", "type": "INTEGER"},
                        {"name": "recordType", "type": "STRING"},
                        {"name": "reportDate", "type": "STRING"},
                    ],
                    "mappers": [],
                    "primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                    "stream": {
                        "default_cursor_field": ["reportDate"],
                        "is_resumable": False,
                        "json_schema": {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "properties": {
                                "metric": {...},
                                "profileId": {...},
                                "recordId": {...},
                                "recordType": {...},
                                "reportDate": {...},
                            },
                            "title": "sponsored_products_report_stream",
                            "type": ["null", "object"],
                        },
                        "name": "sponsored_products_report_stream",
                        "source_defined_cursor": True,
                        "source_defined_primary_key": [["profileId"], ["recordType"], ["reportDate"], ["recordId"]],
                        "supported_sync_modes": ["full_refresh", "incremental"],
                    },
                    "sync_mode": "incremental",
                },
            ]
        },
        state=[
            {
                "stream": {
                    "stream_descriptor": {"name": "profiles", "namespace": None},
                    "stream_state": {"__ab_no_cursor_state_message": True},
                },
                "type": "STREAM",
            },
            {
                "stream": {
                    "stream_descriptor": {"name": "sponsored_brands_v3_report_stream", "namespace": None},
                    "stream_state": {
                        "2575400145671382": {"reportDate": "2025-02-04"},
                    },
                },
                "type": "STREAM",
            },
            {
                "stream": {
                    "stream_descriptor": {"name": "sponsored_products_report_stream", "namespace": None},
                    "stream_state": {
                        "2575400145671382": {"reportDate": "2025-02-04"},
                    },
                },
                "type": "STREAM",
            },
            {
                "stream": {
                    "stream_descriptor": {"name": "sponsored_display_report_stream", "namespace": None},
                    "stream_state": {
                        "2575400145671382": {"reportDate": "2025-02-04"},
                    },
                },
                "type": "STREAM",
            },
        ],
        workspace_id=UUID("90336fed-1595-492e-a938-eaf4b058fb25"),
        destination_docker_image=None,
        destination_id=UUID("97dfd7b1-8908-4f76-af4f-38351fb11fd3"),
        source_config={"key": "value"},
        source_docker_image="airbyte/source-amazon-ads:6.2.7",
        source_id=UUID("93ad83fd-796a-4b5c-bc63-54b0266d28dd"),
        last_attempt_duration_in_microseconds=44902474342,
        streams_with_data=[
            "sponsored_products_report_stream",
            "profiles",
            "sponsored_display_report_stream",
            "sponsored_brands_v3_report_stream",
        ],
    ),
]


def test_get_connection_objects_from_retrieved_objects():
    with (
        patch(
            "live_tests.commons.connection_objects_retrieval.retrieve_testing_candidates",
            return_value=mocking_return_of_retrieve_testing_candidates,
        ),
        patch("live_tests.commons.connection_objects_retrieval.retrieve_objects", return_value=mocking_return_of_retrieve_objects),
    ):
        requested_objects = {
            ConnectionObject.DESTINATION_ID,
            ConnectionObject.SOURCE_ID,
            ConnectionObject.CONFIGURED_CATALOG,
            ConnectionObject.STATE,
            ConnectionObject.CATALOG,
            ConnectionObject.SOURCE_CONFIG,
            ConnectionObject.WORKSPACE_ID,
            ConnectionObject.SOURCE_DOCKER_IMAGE,
        }

        retrieval_reason = "Running live tests on connection for connector airbyte/source-amazon-ads on target versions (dev)."
        selected_streams = {"sponsored_brands_v3_report_stream"}
        connection_objects = _get_connection_objects_from_retrieved_objects(
            requested_objects=requested_objects,
            retrieval_reason=retrieval_reason,
            source_docker_repository="airbyte/source-amazon-ads",
            source_docker_image_tag="6.2.7",
            selected_streams=selected_streams,
            connection_id=None,
            custom_config=None,
            custom_configured_catalog=None,
            custom_state=None,
            connection_subset=ConnectionSubset.ALL,
            max_connections=None,
        )
        # it is expected to get 1 connection only from _find_best_candidates_subset, because selected stream is presented in catalog and has data
        assert len(connection_objects) == 1
        connection_objects_to_check = connection_objects[0]
        assert len(connection_objects_to_check.configured_catalog.streams) == len(
            selected_streams
        ), f"Number of streams in catatalog should match number of selected streams: {len(selected_streams)}"
        assert connection_objects_to_check.configured_catalog.streams[0].stream.name == "sponsored_brands_v3_report_stream"
