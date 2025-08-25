#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from source_google_ads.components import ClickViewHttpRequester, CustomGAQueryHttpRequester, CustomGAQuerySchemaLoader

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader


class TestCustomGAQuerySchemaLoader:
    def test_custom_ga_query_schema_loader_returns_expected_schema(self, config_for_custom_query_tests, requests_mock):
        requests_mock.get(
            "https://googleads.googleapis.com/v20/googleAdsFields/campaign_budget.name",
            json={
                "resourceName": "googleAdsFields/campaign_budget.name",
                "category": "ATTRIBUTE",
                "dataType": "STRING",
                "name": "campaign_budget.name",
                "selectable": True,
                "filterable": True,
                "sortable": True,
                "typeUrl": "",
                "isRepeated": False,
            },
        )
        requests_mock.get(
            "https://googleads.googleapis.com/v20/googleAdsFields/campaign.name",
            json={
                "resourceName": "googleAdsFields/campaign.name",
                "category": "ATTRIBUTE",
                "dataType": "STRING",
                "name": "campaign.name",
                "selectable": True,
                "filterable": True,
                "sortable": True,
                "typeUrl": "",
                "isRepeated": False,
            },
        )
        requests_mock.get(
            "https://googleads.googleapis.com/v20/googleAdsFields/metrics.interaction_event_types",
            json={
                "resourceName": "googleAdsFields/metrics.interaction_event_types",
                "category": "METRIC",
                "dataType": "ENUM",
                "name": "metrics.interaction_event_types",
                "selectable": True,
                "filterable": True,
                "sortable": False,
                "enumValues": ["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"],
                "typeUrl": "google.ads.googleads.v20.enums.InteractionEventTypeEnum.InteractionEventType",
                "isRepeated": True,
            },
        )

        mock_requester = Mock()
        mock_requester.authenticator.get_auth_header.return_value = {}
        config = config_for_custom_query_tests
        config["custom_queries_array"][0]["query"] = (
            "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget"
        )

        schema_loader = CustomGAQuerySchemaLoader(
            config=config, requester=mock_requester, query=config["custom_queries_array"][0]["query"], cursor_field="{{ False }}"
        )

        expected_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": {
                "campaign_budget.name": {"type": ["string", "null"]},
                "campaign.name": {"type": ["string", "null"]},
                "metrics.interaction_event_types": {
                    "type": ["null", "array"],
                    "items": {"type": ["string", "null"], "enum": ["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"]},
                },
            },
        }
        assert schema_loader.get_json_schema() == expected_schema

    def test_custom_ga_query_schema_loader_with_cursor_field_returns_expected_schema(self, config_for_custom_query_tests, requests_mock):
        requests_mock.get(
            "https://googleads.googleapis.com/v20/googleAdsFields/campaign_budget.name",
            json={
                "resourceName": "googleAdsFields/campaign_budget.name",
                "category": "ATTRIBUTE",
                "dataType": "STRING",
                "name": "campaign_budget.name",
                "selectable": True,
                "filterable": True,
                "sortable": True,
                "typeUrl": "",
                "isRepeated": False,
            },
        )
        requests_mock.get(
            "https://googleads.googleapis.com/v20/googleAdsFields/campaign.name",
            json={
                "resourceName": "googleAdsFields/campaign.name",
                "category": "ATTRIBUTE",
                "dataType": "STRING",
                "name": "campaign.name",
                "selectable": True,
                "filterable": True,
                "sortable": True,
                "typeUrl": "",
                "isRepeated": False,
            },
        )
        requests_mock.get(
            "https://googleads.googleapis.com/v20/googleAdsFields/metrics.interaction_event_types",
            json={
                "resourceName": "googleAdsFields/metrics.interaction_event_types",
                "category": "METRIC",
                "dataType": "ENUM",
                "name": "metrics.interaction_event_types",
                "selectable": True,
                "filterable": True,
                "sortable": False,
                "enumValues": ["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"],
                "typeUrl": "google.ads.googleads.v20.enums.InteractionEventTypeEnum.InteractionEventType",
                "isRepeated": True,
            },
        )
        requests_mock.get(
            "https://googleads.googleapis.com/v20/googleAdsFields/segments.date",
            json={
                "resourceName": "googleAdsFields/segments.date",
                "category": "SEGMENT",
                "dataType": "DATE",
                "name": "segments.date",
                "selectable": True,
                "filterable": True,
                "sortable": True,
                "typeUrl": "",
                "isRepeated": False,
            },
        )
        mock_requester = Mock()
        mock_requester.authenticator.get_auth_header.return_value = {}
        schema_loader = CustomGAQuerySchemaLoader(
            config=config_for_custom_query_tests,
            requester=mock_requester,
            query=config_for_custom_query_tests["custom_queries_array"][0]["query"],
            cursor_field=config_for_custom_query_tests["custom_queries_array"][0]["cursor_field"],
        )
        expected_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": {
                "campaign_budget.name": {"type": ["string", "null"]},
                "campaign.name": {"type": ["string", "null"]},
                "metrics.interaction_event_types": {
                    "type": ["null", "array"],
                    "items": {"type": ["string", "null"], "enum": ["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"]},
                },
                "segments.date": {"type": ["string", "null"], "format": "date"},
            },
        }
        assert schema_loader.get_json_schema() == expected_schema

    def test_given_invalid_field_name_raises(self, config_for_custom_query_tests, requests_mock):
        config = config_for_custom_query_tests
        config["custom_queries_array"][0]["query"] = "SELECT invalid_field FROM campaign_budget"
        requests_mock.get(
            "https://googleads.googleapis.com/v20/googleAdsFields/invalid_field",
            json={"error": {"code": 404, "message": "Requested entity was not found.", "status": "NOT_FOUND"}},
        )
        mock_requester = Mock()
        mock_requester.authenticator.get_auth_header.return_value = {}
        schema_loader = CustomGAQuerySchemaLoader(
            config=config_for_custom_query_tests,
            requester=mock_requester,
            query=config_for_custom_query_tests["custom_queries_array"][0]["query"],
            cursor_field="{{ False }}",
        )
        with pytest.raises(AirbyteTracedException) as exc_info:
            schema_loader.get_json_schema()
        assert (
            exc_info.value.message
            == "The provided field is invalid: Status: 'NOT_FOUND', Message: 'Requested entity was not found.', Field: 'invalid_field'"
        )

    @pytest.mark.parametrize(
        "query",
        [
            "campaign.name FROM campaign_budget",
            "SELECT FROM campaign_budget WHERE segments.date = '2021-01-01'",
            "SELECT campaign.name WHERE segments.date '2021-01-01'",
            "SELECT fie ld1, field2 FROM table",
        ],
        ids=["malformed_query_1", "malformed_query_2", "malformed_query_3", "malformed_query_4"],
    )
    def test_given_malformed_query_raises(self, config_for_custom_query_tests, requests_mock, query):
        config = config_for_custom_query_tests
        config["custom_queries_array"][0]["query"] = query
        mock_requester = Mock()
        mock_requester.authenticator.get_auth_header.return_value = {}
        with pytest.raises(AirbyteTracedException) as exc_info:
            CustomGAQuerySchemaLoader(
                config=config, requester=mock_requester, query=config["custom_queries_array"][0]["query"], cursor_field="{{ False }}"
            )


class TestCustomGAQueryHttpRequester:
    def test_given_valid_query_returns_expected_request_body(self, config_for_custom_query_tests, requests_mock):
        config = config_for_custom_query_tests
        config["custom_queries_array"][0]["query"] = (
            "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget"
        )
        requester = CustomGAQueryHttpRequester(
            name="test_custom_ga_query_http_requester",
            parameters={
                "query": config["custom_queries_array"][0]["query"],
                "cursor_field": "{{ False }}",
            },
            config=config,
        )
        request_body = requester.get_request_body_json(stream_slice={})
        assert request_body == {"query": "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget"}

    def test_given_valid_query_with_cursor_field_returns_expected_request_body(self, config_for_custom_query_tests, requests_mock):
        config = config_for_custom_query_tests
        config["custom_queries_array"][0]["query"] = (
            "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget"
        )
        requester = CustomGAQueryHttpRequester(
            name="test_custom_ga_query_http_requester",
            parameters={
                "query": config["custom_queries_array"][0]["query"],
                "cursor_field": config["custom_queries_array"][0]["cursor_field"],
            },
            config=config,
        )
        request_body = requester.get_request_body_json(
            stream_slice={
                "customer_id": "customers/123",
                "parent_slice": {"customer_id": "123", "parent_slice": {}},
                "start_time": "2025-07-18",
                "end_time": "2025-07-19",
            }
        )
        assert request_body == {
            "query": "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types, segments.date FROM campaign_budget WHERE segments.date BETWEEN '2025-07-18' AND '2025-07-19' ORDER BY segments.date ASC"
        }


class TestClickViewHttpRequester:
    def test_click_view_http_requester_returns_expected_request_body(self, config):
        requester = ClickViewHttpRequester(
            name="test_click_view_http_requester",
            parameters={},
            config=config,
            schema_loader=InlineSchemaLoader(
                schema={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "ad_group.name": {"description": "The name of the ad group.", "type": ["null", "string"]},
                        "click_view.gclid": {
                            "description": "The Google Click Identifier for tracking purposes.",
                            "type": ["null", "string"],
                        },
                        "click_view.ad_group_ad": {
                            "description": "Details of the ad in the ad group that was clicked.",
                            "type": ["null", "string"],
                        },
                        "segments.date": {"description": "The date when the click occurred.", "type": ["null", "string"], "format": "date"},
                    },
                },
                parameters={},
            ),
        )
        request_body = requester.get_request_body_json(
            stream_slice={
                "customer_id": "customers/123",
                "parent_slice": {"customer_id": "123", "parent_slice": {}},
                "start_time": "2025-07-18",
                "end_time": "2025-07-19",
            }
        )
        assert request_body == {
            "query": "SELECT ad_group.name, click_view.gclid, click_view.ad_group_ad, segments.date FROM click_view WHERE segments.date = '2025-07-18'"
        }
