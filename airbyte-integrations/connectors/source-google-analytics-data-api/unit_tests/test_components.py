#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from typing import Dict, List, Union

import pytest
import yaml


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


def _load_manifest():
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return yaml.safe_load(manifest_path.read_text())


def test_complete_oauth_output_specification_does_not_include_access_token():
    """Verify that complete_oauth_output_specification only maps refresh_token.

    extract_output only extracts refresh_token from the OAuth token exchange,
    so access_token would always be null. Mapping it in the output spec causes
    a schema validation failure (null found, string expected) when creating a
    source via the API with a secretId.
    """
    manifest = _load_manifest()
    oauth_config = manifest["spec"]["advanced_auth"]["oauth_config_specification"]
    output_spec = oauth_config["complete_oauth_output_specification"]
    properties = output_spec["properties"]

    assert "access_token" not in properties, (
        "access_token must not appear in complete_oauth_output_specification "
        "because extract_output only extracts refresh_token"
    )
    assert "refresh_token" in properties


def test_extract_output_and_oauth_output_spec_are_consistent():
    """Verify every field in complete_oauth_output_specification is also in extract_output."""
    manifest = _load_manifest()
    oauth_config = manifest["spec"]["advanced_auth"]["oauth_config_specification"]
    oauth_input = oauth_config["oauth_connector_input_specification"]
    extract_output = set(oauth_input["extract_output"])
    output_spec = oauth_config["complete_oauth_output_specification"]
    output_properties = set(output_spec["properties"].keys())

    assert output_properties.issubset(extract_output), (
        f"complete_oauth_output_specification maps {output_properties - extract_output} "
        f"which are not in extract_output {extract_output}"
    )
