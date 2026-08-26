#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from typing import Dict, List, Union

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.transformations.config_transformations.add_fields import ConfigAddFields
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "credentials": {"auth_type": "Client", "client_id": "cred", "client_secret": "secret", "refresh_token": "token"},
    "date_ranges_start_date": "2025-04-01",
    "date_ranges_end_date": "2025-10-01",
    "window_in_days": 1,
    "property_ids": ["12345"],
    "custom_reports_array": [
        {
            "name": "cohort_report",
            "dimensions": ["cohort", "cohortNthDay"],
            "metrics": ["cohortActiveUsers"],
            "cohortSpec": {
                "cohorts": [{"dimension": "firstSessionDate", "dateRange": {"startDate": "2023-04-24", "endDate": "2023-04-24"}}],
                "cohortsRange": {"endOffset": 100, "granularity": "DAILY"},
                "cohortReportSettings": {"accumulate": False},
                "enabled": "true",
            },
        }
    ],
}


@pytest.mark.parametrize(
    "dimension_filter, expected_transformed_dimension_filter",
    [
        pytest.param(
            {
                "filter": {"value": "United States", "matchType": ["EXACT"], "filter_name": "stringFilter", "caseSensitive": True},
                "field_name": "country",
                "filter_type": "filter",
            },
            {"filter": {"fieldName": "country", "stringFilter": {"value": "United States", "matchType": "EXACT", "caseSensitive": True}}},
            id="test_string_filter",
        ),
        pytest.param(
            {
                "filter": {"values": ["value_0", "value_1"], "filter_name": "inListFilter", "caseSensitive": False},
                "field_name": "country",
                "filter_type": "filter",
            },
            {"filter": {"fieldName": "country", "inListFilter": {"values": ["value_0", "value_1"], "caseSensitive": False}}},
            id="test_in_list_filter",
        ),
        pytest.param(
            {
                "filter": {
                    "value": {"value_type": "int64Value", "value": 100},
                    "operation": ["GREATER_THAN"],
                    "filter_name": "numericFilter",
                },
                "field_name": "sessions",
                "filter_type": "filter",
            },
            {"filter": {"fieldName": "sessions", "numericFilter": {"value": {"int64Value": 100}, "operation": "GREATER_THAN"}}},
            id="test_numeric_filter",
        ),
        pytest.param(
            {
                "filter": {
                    "fromValue": {"value_type": "doubleValue", "value": "10.5"},
                    "toValue": {"value_type": "doubleValue", "value": "20.7"},
                    "filter_name": "betweenFilter",
                },
                "field_name": "revenue",
                "filter_type": "filter",
            },
            {"filter": {"fieldName": "revenue", "betweenFilter": {"fromValue": {"doubleValue": 10.5}, "toValue": {"doubleValue": 20.7}}}},
            id="test_between_filter",
        ),
    ],
)
def test_dimension_filter_config_transformation(components_module, dimension_filter, expected_transformed_dimension_filter):
    dimension_filter_config_transformation = components_module.DimensionFilterConfigTransformation()

    config = _CONFIG.copy()
    config["custom_reports_array"][0] = {
        "name": "custom_report",
        "dateRanges": [{"startDate": "2025-04-01", "endDate": "2025-10-01"}],
        "dimensions": ["country"],
        "metrics": ["sessions"],
        "dimensionFilter": dimension_filter,
        "cohortSpec": {"enabled": "false"},
    }

    dimension_filter_config_transformation.transform(config)

    assert config["custom_reports_array"][0]["dimensionFilter"] == expected_transformed_dimension_filter


def test_no_dimension_filter_config_transformation(components_module):
    dimension_filter_config_transformation = components_module.DimensionFilterConfigTransformation()

    config = _CONFIG.copy()
    config["custom_reports_array"][0] = {
        "name": "custom_report",
        "dateRanges": [{"startDate": "2025-04-01", "endDate": "2025-10-01"}],
        "dimensions": ["country"],
        "metrics": ["sessions"],
        "cohortSpec": {"enabled": "false"},
    }

    dimension_filter_config_transformation.transform(config)

    assert "dimensionFilter" not in config["custom_reports_array"][0]


def test_no_custom_report_dimension_filter_config_transformation(components_module):
    dimension_filter_config_transformation = components_module.DimensionFilterConfigTransformation()

    config = _CONFIG.copy()
    del config["custom_reports_array"]

    dimension_filter_config_transformation.transform(config)

    assert "custom_reports_array" not in config


def test_dynamic_stream_naming_preserves_nested_name(manifest_path):
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["definitions"]["streams"]["google_analytics_stream_template"]["retriever"]["requester"]["request_parameters"] = {
        "name": "keep-me"
    }
    config = {"property_ids": ["111", "222"]}

    source = ConcurrentDeclarativeSource(source_config=manifest, config=config)
    resolved_streams = source._dynamic_stream_configs(source._source_config)

    assert all(stream["retriever"]["requester"]["request_parameters"]["name"] == "keep-me" for stream in resolved_streams)
    assert [stream["name"] for stream in resolved_streams[:2]] == [
        "daily_active_users",
        "daily_active_usersProperty222",
    ]


@pytest.mark.parametrize(
    "filter_type, expected_transformed_dimension_filter",
    [
        pytest.param(
            "andGroup",
            {
                "andGroup": {
                    "expressions": [
                        {
                            "filter": {
                                "fieldName": "country",
                                "stringFilter": {"value": "United States", "matchType": "EXACT", "caseSensitive": True},
                            }
                        },
                        {"filter": {"fieldName": "sessions", "numericFilter": {"value": {"int64Value": 100}, "operation": "GREATER_THAN"}}},
                    ]
                }
            },
            id="test_and_group",
        ),
        pytest.param(
            "orGroup",
            {
                "orGroup": {
                    "expressions": [
                        {
                            "filter": {
                                "fieldName": "country",
                                "stringFilter": {"value": "United States", "matchType": "EXACT", "caseSensitive": True},
                            }
                        },
                        {"filter": {"fieldName": "sessions", "numericFilter": {"value": {"int64Value": 100}, "operation": "GREATER_THAN"}}},
                    ]
                }
            },
            id="test_or_group",
        ),
    ],
)
def test_groups_dimension_filter_config_transformation(components_module, filter_type, expected_transformed_dimension_filter):
    dimension_filter_config_transformation = components_module.DimensionFilterConfigTransformation()

    config = _CONFIG.copy()
    config["custom_reports_array"][0] = {
        "name": "custom_report",
        "dateRanges": [{"startDate": "2025-04-01", "endDate": "2025-10-01"}],
        "dimensions": ["country"],
        "metrics": ["sessions"],
        "dimensionFilter": {
            "filter_type": filter_type,
            "expressions": [
                {
                    "field_name": "country",
                    "filter": {"filter_name": "stringFilter", "value": "United States", "matchType": ["EXACT"], "caseSensitive": True},
                },
                {
                    "field_name": "sessions",
                    "filter": {
                        "filter_name": "numericFilter",
                        "value": {"value_type": "int64Value", "value": 100},
                        "operation": ["GREATER_THAN"],
                    },
                },
            ],
        },
        "cohortSpec": {"enabled": "false"},
    }

    dimension_filter_config_transformation.transform(config)

    assert config["custom_reports_array"][0]["dimensionFilter"] == expected_transformed_dimension_filter


def test_not_expression_dimension_filter_config_transformation(components_module):
    dimension_filter_config_transformation = components_module.DimensionFilterConfigTransformation()

    config = _CONFIG.copy()
    config["custom_reports_array"][0] = {
        "name": "custom_report",
        "dateRanges": [{"startDate": "2025-04-01", "endDate": "2025-10-01"}],
        "dimensions": ["country"],
        "metrics": ["sessions"],
        "dimensionFilter": {
            "filter_type": "notExpression",
            "expression": {
                "field_name": "country",
                "filter": {"filter_name": "stringFilter", "value": "United States", "matchType": ["EXACT"], "caseSensitive": True},
            },
        },
        "cohortSpec": {"enabled": "false"},
    }

    dimension_filter_config_transformation.transform(config)

    expected_dimension_filter = {
        "notExpression": {
            "filter": {"fieldName": "country", "stringFilter": {"value": "United States", "matchType": "EXACT", "caseSensitive": True}}
        }
    }

    assert config["custom_reports_array"][0]["dimensionFilter"] == expected_dimension_filter


@pytest.mark.parametrize(
    "credentials,expected_auth_type",
    [
        pytest.param(
            {"client_id": "cid", "client_secret": "cs", "refresh_token": "rt"},
            "Client",
            id="oauth_creds_without_auth_type_infers_Client",
        ),
        pytest.param(
            {"credentials_json": '{"type":"service_account"}'},
            "Service",
            id="service_account_creds_without_auth_type_infers_Service",
        ),
        pytest.param(
            {"auth_type": "Client", "client_id": "cid", "client_secret": "cs", "refresh_token": "rt"},
            "Client",
            id="oauth_creds_with_auth_type_preserves_Client",
        ),
        pytest.param(
            {"auth_type": "Service", "credentials_json": '{"type":"service_account"}'},
            "Service",
            id="service_account_creds_with_auth_type_preserves_Service",
        ),
    ],
)
def test_config_normalization_infers_auth_type(credentials, expected_auth_type):
    """Verify that config normalization sets auth_type when OAuth or Service Account
    credentials are present but auth_type is missing.

    Regression test for https://github.com/airbytehq/oncall/issues/12125
    """
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())

    transformations = manifest["spec"]["config_normalization_rules"]["transformations"]
    add_fields_defs = [t for t in transformations if t.get("type") == "ConfigAddFields"]

    config = {"credentials": credentials, "property_ids": ["12345"]}

    for add_field_def in add_fields_defs:
        field_defs = [
            AddedFieldDefinition(path=f["path"], value=f["value"], value_type=None, parameters={}) for f in add_field_def["fields"]
        ]
        transformation = ConfigAddFields(fields=field_defs, condition=add_field_def.get("condition", ""))
        transformation.transform(config)

    assert config["credentials"]["auth_type"] == expected_auth_type


def test_config_normalization_no_credentials_does_not_add_auth_type():
    """Verify that config normalization does not add auth_type when no credentials are present."""
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())

    transformations = manifest["spec"]["config_normalization_rules"]["transformations"]
    add_fields_defs = [t for t in transformations if t.get("type") == "ConfigAddFields"]

    config = {"property_ids": ["12345"]}

    for add_field_def in add_fields_defs:
        field_defs = [
            AddedFieldDefinition(path=f["path"], value=f["value"], value_type=None, parameters={}) for f in add_field_def["fields"]
        ]
        transformation = ConfigAddFields(fields=field_defs, condition=add_field_def.get("condition", ""))
        transformation.transform(config)

    assert "credentials" not in config


def test_complete_oauth_output_specification_contains_refresh_and_access_token():
    """Verify that complete_oauth_output_specification declares both refresh_token and access_token,
    and that extract_output matches.

    Both tokens must be listed so the platform correctly merges the OAuth response into the
    connector config when users create sources via the public API with secretId.

    Regression test for https://github.com/airbytehq/oncall/issues/11935
    """
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())

    oauth_spec = manifest["spec"]["advanced_auth"]["oauth_config_specification"]

    # extract_output should list both refresh_token and access_token
    extract_output = oauth_spec["oauth_connector_input_specification"]["extract_output"]
    assert "refresh_token" in extract_output, "refresh_token must be in extract_output"
    assert "access_token" in extract_output, "access_token must be in extract_output"

    # complete_oauth_output_specification must match extract_output
    output_props = oauth_spec["complete_oauth_output_specification"]["properties"]
    assert "refresh_token" in output_props, "refresh_token must be in complete_oauth_output_specification"
    assert "access_token" in output_props, "access_token must be in complete_oauth_output_specification"


def test_dynamic_stream_paginates_run_report_results():
    """Verify that dynamic runReport streams paginate with GA4 body parameters."""
    config = {
        "credentials": {"auth_type": "Client", "client_id": "cid", "client_secret": "secret", "refresh_token": "refresh"},
        "property_ids": ["12345"],
        "custom_reports_array": [{"name": "large_report", "dimensions": ["date"], "metrics": ["sessions"]}],
        "date_ranges_start_date": "2025-01-01",
        "date_ranges_end_date": "2025-01-02",
        "window_in_days": 1,
    }
    source = YamlDeclarativeSource(str(Path(__file__).parent.parent / "manifest.yaml"), config=config)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="large_report",
                    json_schema={
                        "type": "object",
                        "properties": {"date": {"type": "string"}, "sessions": {"type": "integer"}},
                    },
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )
    report_url = "https://analyticsdata.googleapis.com/v1beta/properties/12345:runReport"
    request_bodies = []

    def report_callback(request, context):
        request_body = request.json()
        request_bodies.append(request_body)
        offset = request_body.get("offset", 0)
        rows = [
            {"dimensionValues": [{"value": str(offset + index)}], "metricValues": [{"value": str(offset + index)}]}
            for index in range(25000 if offset == 0 else 1)
        ]
        return {
            "dimensionHeaders": [{"name": "date"}],
            "metricHeaders": [{"name": "sessions"}],
            "rows": rows,
        }

    with requests_mock.Mocker() as http_mock:
        http_mock.post("https://www.googleapis.com/oauth2/v4/token", json={"access_token": "token", "expires_in": 3600})
        http_mock.get(
            "https://analyticsdata.googleapis.com/v1beta/properties/12345/metadata",
            json={"metrics": [{"apiName": "sessions", "type": "TYPE_INTEGER"}]},
        )
        http_mock.post(report_url, json=report_callback)
        output = read(source, config, catalog)

    output.raise_if_errors()
    assert len(output.records) == 25001
    assert len(request_bodies) == 2
    assert request_bodies[0]["limit"] == 25000
    assert "offset" not in request_bodies[0]
    assert request_bodies[1]["limit"] == 25000
    assert request_bodies[1]["offset"] == 25000


def test_dynamic_stream_orders_paged_run_report_requests_by_every_dimension():
    """Offset pagination is only safe when the row order is stable, so every paged request must
    carry the same total ordering over all configured dimensions."""
    dimensions = ["date", "country", "deviceCategory"]
    config = {
        "credentials": {"auth_type": "Client", "client_id": "cid", "client_secret": "secret", "refresh_token": "refresh"},
        "property_ids": ["12345"],
        "custom_reports_array": [{"name": "large_report", "dimensions": dimensions, "metrics": ["sessions"]}],
        "date_ranges_start_date": "2025-01-01",
        "date_ranges_end_date": "2025-01-02",
        "window_in_days": 1,
    }
    source = YamlDeclarativeSource(str(Path(__file__).parent.parent / "manifest.yaml"), config=config)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="large_report",
                    json_schema={
                        "type": "object",
                        "properties": {
                            **{dimension: {"type": "string"} for dimension in dimensions},
                            "sessions": {"type": "integer"},
                        },
                    },
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )
    report_url = "https://analyticsdata.googleapis.com/v1beta/properties/12345:runReport"
    request_bodies = []

    def report_callback(request, context):
        request_body = request.json()
        request_bodies.append(request_body)
        offset = request_body.get("offset", 0)
        rows = [
            {
                "dimensionValues": [{"value": str(offset + index)} for _ in dimensions],
                "metricValues": [{"value": str(offset + index)}],
            }
            for index in range(25000 if offset == 0 else 1)
        ]
        return {
            "dimensionHeaders": [{"name": dimension} for dimension in dimensions],
            "metricHeaders": [{"name": "sessions"}],
            "rows": rows,
        }

    with requests_mock.Mocker() as http_mock:
        http_mock.post("https://www.googleapis.com/oauth2/v4/token", json={"access_token": "token", "expires_in": 3600})
        http_mock.get(
            "https://analyticsdata.googleapis.com/v1beta/properties/12345/metadata",
            json={"metrics": [{"apiName": "sessions", "type": "TYPE_INTEGER"}]},
        )
        http_mock.post(report_url, json=report_callback)
        output = read(source, config, catalog)

    output.raise_if_errors()
    expected_order_bys = [{"dimension": {"dimensionName": dimension}} for dimension in dimensions]
    assert len(request_bodies) == 2
    assert "offset" not in request_bodies[0]
    assert request_bodies[1]["offset"] == 25000
    assert [body["orderBys"] for body in request_bodies] == [expected_order_bys, expected_order_bys]



@pytest.mark.parametrize(
    "custom_report, expected_order_bys",
    [
        pytest.param(
            {"name": "report", "dimensions": ["date", "country"], "metrics": ["sessions"]},
            [{"dimension": {"dimensionName": "date"}}, {"dimension": {"dimensionName": "country"}}],
            id="every_dimension_is_ordered",
        ),
        pytest.param(
            {"name": "report", "dimensions": [], "metrics": ["sessions"]},
            None,
            id="metric_only_report_omits_order_bys",
        ),
        pytest.param(
            {
                "name": "report",
                "dimensions": ["cohort", "cohortNthDay"],
                "metrics": ["cohortActiveUsers"],
                "cohortSpec": {
                    "cohorts": [{"dimension": "firstSessionDate", "dateRange": {"startDate": "2023-04-24", "endDate": "2023-04-24"}}],
                    "cohortsRange": {"endOffset": 100, "granularity": "DAILY"},
                    "enabled": "true",
                },
            },
            None,
            id="cohort_report_omits_order_bys",
        ),
        pytest.param(
            {
                "name": "report",
                "dimensions": ["country"],
                "metrics": ["sessions"],
                "pivots": [{"fieldNames": ["date"], "limit": 1, "offset": 0}],
            },
            None,
            id="pivot_report_omits_top_level_order_bys",
        ),
    ],
)
def test_run_report_order_bys(manifest_path, custom_report, expected_order_bys):
    """`orderBys` must cover every dimension for paginated runReport requests, and must be absent
    where GA4 either does not accept it (pivot requests) or does not document it (cohorts), and
    where there is nothing to order by."""
    manifest = yaml.safe_load(manifest_path.read_text())
    config = {"property_ids": ["12345"], "custom_reports_array": [custom_report]}

    source = ConcurrentDeclarativeSource(source_config=manifest, config=config)
    resolved_streams = source._dynamic_stream_configs(source._source_config)

    stream = next(stream for stream in resolved_streams if stream["name"] == "report")
    assert stream["retriever"]["requester"]["request_body_json"].get("orderBys") == expected_order_bys


def test_dynamic_pivot_streams_disable_pagination():
    """Verify that dynamic pivot streams preserve GA4's no-pagination behavior."""
    config = {
        "credentials": {"auth_type": "Client", "client_id": "cid", "client_secret": "secret", "refresh_token": "refresh"},
        "property_ids": ["12345"],
        "custom_reports_array": [
            {
                "name": "pivot_report",
                "dimensions": ["country"],
                "metrics": ["sessions"],
                "pivots": [{"fieldNames": ["date"], "limit": 1, "offset": 0}],
            }
        ],
    }
    source = YamlDeclarativeSource(str(Path(__file__).parent.parent / "manifest.yaml"), config=config)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="pivot_report",
                    json_schema={"type": "object", "properties": {"country": {"type": "string"}, "sessions": {"type": "integer"}}},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )
    report_url = "https://analyticsdata.googleapis.com/v1beta/properties/12345:runPivotReport"
    request_bodies = []

    def report_callback(request, context):
        request_bodies.append(request.json())
        return {
            "dimensionHeaders": [{"name": "country"}],
            "metricHeaders": [{"name": "sessions"}],
            "rows": [{"dimensionValues": [{"value": "US"}], "metricValues": [{"value": "1"}]}],
        }

    with requests_mock.Mocker() as http_mock:
        http_mock.post("https://www.googleapis.com/oauth2/v4/token", json={"access_token": "token", "expires_in": 3600})
        http_mock.get(
            "https://analyticsdata.googleapis.com/v1beta/properties/12345/metadata",
            json={"metrics": [{"apiName": "sessions", "type": "TYPE_INTEGER"}]},
        )
        http_mock.post(report_url, json=report_callback)
        output = read(source, config, catalog)

    output.raise_if_errors()
    assert len(request_bodies) == 1
    assert "offset" not in request_bodies[0]
    # RunPivotReportRequest has no top-level `orderBys` field; pivot ordering lives inside each pivot.
    assert "orderBys" not in request_bodies[0]
