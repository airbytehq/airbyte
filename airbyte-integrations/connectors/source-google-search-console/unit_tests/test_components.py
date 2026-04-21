# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize(
    "stream_state,expected_should_migrate,expected_migrated_state",
    [
        pytest.param(
            {
                "date": "2025-05-14",
                "https://evangelion.com": {"web": {"date": "2025-05-30"}, "news": {"date": "2025-05-23"}, "image": {"date": "2025-05-16"}},
                "https://nerv.gov": {"web": {"date": "2025-05-28"}, "news": {"date": "2025-05-21"}, "image": {"date": "2025-05-14"}},
            },
            True,
            {
                "use_global_cursor": False,
                "states": [
                    {"partition": {"search_type": "web", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-30"}},
                    {"partition": {"search_type": "news", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-23"}},
                    {"partition": {"search_type": "image", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-16"}},
                    {"partition": {"search_type": "web", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-28"}},
                    {"partition": {"search_type": "news", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-21"}},
                    {"partition": {"search_type": "image", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-14"}},
                ],
            },
            id="test_migrate_legacy_state_to_per_partition_state",
        ),
        pytest.param(
            {
                "use_global_cursor": False,
                "states": [
                    {"partition": {"search_type": "web", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-30"}},
                    {"partition": {"search_type": "news", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-23"}},
                    {"partition": {"search_type": "image", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-16"}},
                    {"partition": {"search_type": "web", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-28"}},
                    {"partition": {"search_type": "news", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-21"}},
                    {"partition": {"search_type": "image", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-14"}},
                ],
                "state": {"date": "2025-05-14"},
            },
            False,
            None,
            id="test_do_not_migrate_if_already_per_partition_state",
        ),
        pytest.param({}, False, None, id="test_do_not_migrate_empty_state"),
    ],
)
def test_nested_substream(stream_state, expected_should_migrate, expected_migrated_state, components_module):
    component = components_module.NestedSubstreamStateMigration()

    should_migrate = component.should_migrate(stream_state=stream_state)
    assert should_migrate == expected_should_migrate

    if should_migrate:
        migrated_state = component.migrate(stream_state=stream_state)
        assert migrated_state == expected_migrated_state


def test_custom_report_extract_dimensions_from_keys(components_module):
    expected_record = {
        "clicks": 0,
        "impressions": 1,
        "ctr": 0,
        "position": 11,
        "site_url": "sc-domain:airbyte.io",
        "search_type": "web",
        "date": "2025-05-28",
        "country": "usa",
        "device": "desktop",
    }

    component = components_module.CustomReportExtractDimensionsFromKeys(dimensions=["date", "country", "device"])

    record = {
        "clicks": 0,
        "impressions": 1,
        "ctr": 0,
        "position": 11,
        "site_url": "sc-domain:airbyte.io",
        "search_type": "web",
        "keys": ["2025-05-28", "usa", "desktop"],
    }
    component.transform(record=record)

    assert record == expected_record


def test_custom_report_schema_loader(components_module):
    expected_schema = {
        "$schema": "https://json-schema.org/draft-07/schema#",
        "type": ["null", "object"],
        "additionalProperties": True,
        "properties": {
            "clicks": {"type": ["null", "integer"]},
            "impressions": {"type": ["null", "integer"]},
            "ctr": {"type": ["null", "number"], "multipleOf": 1e-25},
            "position": {"type": ["null", "number"], "multipleOf": 1e-25},
            "site_url": {"type": ["null", "string"]},
            "search_type": {"type": ["null", "string"]},
            "date": {"type": ["null", "string"], "format": "date"},
            "country": {"type": ["null", "string"]},
            "device": {"type": ["null", "string"]},
            "page": {"type": ["null", "string"]},
            "query": {"type": ["null", "string"]},
        },
    }

    schema_loader = components_module.CustomReportSchemaLoader(dimensions=["date", "country", "device", "page", "query"])

    actual_schema = schema_loader.get_json_schema()

    assert actual_schema == expected_schema


class TestSanitizeNumericFields:
    """Tests for the SanitizeNumericFields transformation."""

    def test_complex_values_are_sanitized(self, components_module):
        """Complex values in numeric fields should be replaced with their real component."""
        component = components_module.SanitizeNumericFields()
        record = {
            "clicks": complex(42, 0),
            "impressions": complex(100, 0),
            "ctr": complex(0.0423, 0),
            "position": complex(3.7, 0),
            "site_url": "https://example.com",
        }
        component.transform(record=record)

        assert record["clicks"] == 42.0
        assert record["impressions"] == 100.0
        assert record["ctr"] == 0.0423
        assert record["position"] == 3.7
        assert isinstance(record["clicks"], float)
        assert isinstance(record["ctr"], float)
        # Non-numeric fields should be untouched
        assert record["site_url"] == "https://example.com"

    def test_normal_values_are_not_modified(self, components_module):
        """Regular int/float values should pass through unchanged."""
        component = components_module.SanitizeNumericFields()
        record = {
            "clicks": 10,
            "impressions": 500,
            "ctr": 0.02,
            "position": 4.5,
        }
        component.transform(record=record)

        assert record["clicks"] == 10
        assert record["impressions"] == 500
        assert record["ctr"] == 0.02
        assert record["position"] == 4.5

    def test_none_values_are_not_modified(self, components_module):
        """None values in numeric fields should not be touched."""
        component = components_module.SanitizeNumericFields()
        record = {
            "clicks": None,
            "impressions": None,
            "ctr": None,
            "position": None,
        }
        component.transform(record=record)

        assert record["clicks"] is None
        assert record["impressions"] is None
        assert record["ctr"] is None
        assert record["position"] is None

    def test_missing_fields_are_ignored(self, components_module):
        """Records without numeric metric fields should not raise errors."""
        component = components_module.SanitizeNumericFields()
        record = {"site_url": "https://example.com", "search_type": "web"}
        component.transform(record=record)

        assert record == {"site_url": "https://example.com", "search_type": "web"}

    def test_complex_with_nonzero_imaginary_uses_real(self, components_module):
        """Even if the imaginary part is nonzero, only the real part should be extracted."""
        component = components_module.SanitizeNumericFields()
        record = {
            "clicks": complex(5, 3),
            "impressions": 100,
            "ctr": complex(0.05, 0.01),
            "position": 2.0,
        }
        component.transform(record=record)

        assert record["clicks"] == 5.0
        assert record["ctr"] == 0.05
        # Non-complex fields remain unchanged
        assert record["impressions"] == 100
        assert record["position"] == 2.0

    def test_warning_logged_for_complex_values(self, components_module, caplog):
        """A warning should be logged when a complex value is encountered."""
        component = components_module.SanitizeNumericFields()
        record = {"clicks": complex(42, 0), "impressions": 100, "ctr": 0.5, "position": 1.0}

        with caplog.at_level(logging.WARNING, logger="airbyte"):
            component.transform(record=record)

        assert any("Complex value encountered for field 'clicks'" in msg for msg in caplog.messages)


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
