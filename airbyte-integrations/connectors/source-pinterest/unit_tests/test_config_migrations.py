#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""
Tests for the config migration that converts window_days fields from array to integer.

Prior versions of source-pinterest incorrectly declared default: [30] (array) for
engagement_window_days and view_window_days in the custom_reports spec. This caused
saved configs to contain array values (e.g. [30]) instead of integers (30).

The ConfigMigration in manifest.yaml should automatically convert these array values
back to integers on config load.
"""

from pathlib import Path
from typing import Any, Dict, List

import yaml

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


def _load_migration_template() -> str:
    """Load the config migration Jinja template from the manifest."""
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)

    config_migrations = manifest["spec"]["config_normalization_rules"]["config_migrations"]
    assert len(config_migrations) >= 1, "Expected at least one config migration"

    migration = config_migrations[0]
    assert migration["type"] == "ConfigMigration"

    transformations = migration["transformations"]
    assert len(transformations) >= 1, "Expected at least one transformation"

    add_fields = transformations[0]
    assert add_fields["type"] == "ConfigAddFields"

    fields = add_fields["fields"]
    assert len(fields) >= 1, "Expected at least one field"
    assert fields[0]["path"] == ["custom_reports"]

    return fields[0]["value"], add_fields.get("condition", "")


def _evaluate_migration(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluate the migration Jinja template against a config and return the migrated custom_reports."""
    template, condition = _load_migration_template()
    interpolation = JinjaInterpolation()

    # Check if the condition evaluates to true
    if condition:
        condition_result = interpolation.eval(condition, config)
        if not condition_result:
            # Migration should not apply; return original custom_reports
            return config.get("custom_reports", [])

    result = interpolation.eval(template, config)
    return result


class TestConfigMigrationWindowDays:
    """Tests for the window_days array-to-integer config migration."""

    def test_migration_converts_array_engagement_window_days_to_integer(self):
        """engagement_window_days: [30] should be migrated to 30."""
        config = {
            "custom_reports": [
                {
                    "name": "test_report",
                    "level": "ADVERTISER",
                    "granularity": "TOTAL",
                    "columns": ["IMPRESSION_1"],
                    "engagement_window_days": [30],
                }
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 1
        assert result[0]["engagement_window_days"] == 30
        assert isinstance(result[0]["engagement_window_days"], int)

    def test_migration_converts_array_view_window_days_to_integer(self):
        """view_window_days: [30] should be migrated to 30."""
        config = {
            "custom_reports": [
                {
                    "name": "test_report",
                    "level": "ADVERTISER",
                    "granularity": "TOTAL",
                    "columns": ["IMPRESSION_1"],
                    "view_window_days": [30],
                }
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 1
        assert result[0]["view_window_days"] == 30
        assert isinstance(result[0]["view_window_days"], int)

    def test_migration_converts_array_click_window_days_to_integer(self):
        """click_window_days: [7] should be migrated to 7."""
        config = {
            "custom_reports": [
                {
                    "name": "test_report",
                    "level": "ADVERTISER",
                    "granularity": "TOTAL",
                    "columns": ["IMPRESSION_1"],
                    "click_window_days": [7],
                }
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 1
        assert result[0]["click_window_days"] == 7
        assert isinstance(result[0]["click_window_days"], int)

    def test_migration_preserves_integer_window_days(self):
        """Already-correct integer values should not be changed."""
        config = {
            "custom_reports": [
                {
                    "name": "test_report",
                    "level": "ADVERTISER",
                    "granularity": "TOTAL",
                    "columns": ["IMPRESSION_1"],
                    "click_window_days": 30,
                    "engagement_window_days": 14,
                    "view_window_days": 7,
                }
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 1
        assert result[0]["click_window_days"] == 30
        assert result[0]["engagement_window_days"] == 14
        assert result[0]["view_window_days"] == 7

    def test_migration_preserves_zero_window_days(self):
        """Zero is a valid enum value and should be preserved."""
        config = {
            "custom_reports": [
                {
                    "name": "test_report",
                    "level": "ADVERTISER",
                    "granularity": "TOTAL",
                    "columns": ["IMPRESSION_1"],
                    "click_window_days": 0,
                    "engagement_window_days": 0,
                    "view_window_days": 0,
                }
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 1
        assert result[0]["click_window_days"] == 0
        assert result[0]["engagement_window_days"] == 0
        assert result[0]["view_window_days"] == 0

    def test_migration_handles_multiple_reports(self):
        """Migration should process all reports in the custom_reports array."""
        config = {
            "custom_reports": [
                {
                    "name": "report_1",
                    "level": "ADVERTISER",
                    "granularity": "TOTAL",
                    "columns": ["IMPRESSION_1"],
                    "engagement_window_days": [30],
                    "view_window_days": [14],
                },
                {
                    "name": "report_2",
                    "level": "CAMPAIGN",
                    "granularity": "DAY",
                    "columns": ["SPEND_IN_DOLLAR"],
                    "engagement_window_days": 7,
                    "view_window_days": [60],
                    "click_window_days": [1],
                },
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 2

        # First report
        assert result[0]["name"] == "report_1"
        assert result[0]["engagement_window_days"] == 30
        assert result[0]["view_window_days"] == 14

        # Second report
        assert result[1]["name"] == "report_2"
        assert result[1]["engagement_window_days"] == 7  # already integer, preserved
        assert result[1]["view_window_days"] == 60
        assert result[1]["click_window_days"] == 1

    def test_migration_preserves_non_window_fields(self):
        """All non-window_days fields should be preserved unchanged."""
        config = {
            "custom_reports": [
                {
                    "name": "my_report",
                    "level": "AD_GROUP",
                    "granularity": "WEEK",
                    "columns": ["IMPRESSION_1", "SPEND_IN_DOLLAR"],
                    "conversion_report_time": "TIME_OF_CONVERSION",
                    "attribution_types": ["INDIVIDUAL", "HOUSEHOLD"],
                    "start_date": "2024-01-01",
                    "engagement_window_days": [30],
                }
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 1
        report = result[0]
        assert report["name"] == "my_report"
        assert report["level"] == "AD_GROUP"
        assert report["granularity"] == "WEEK"
        assert report["columns"] == ["IMPRESSION_1", "SPEND_IN_DOLLAR"]
        assert report["conversion_report_time"] == "TIME_OF_CONVERSION"
        assert report["attribution_types"] == ["INDIVIDUAL", "HOUSEHOLD"]
        assert report["start_date"] == "2024-01-01"
        assert report["engagement_window_days"] == 30

    def test_migration_skips_when_no_custom_reports(self):
        """Migration should not apply when custom_reports is absent."""
        config = {
            "client_id": "test",
            "client_secret": "test",
            "refresh_token": "test",
        }
        result = _evaluate_migration(config)
        # Should return empty list since no custom_reports
        assert result == []

    def test_migration_handles_report_without_window_days(self):
        """Reports that don't set window_days fields should pass through unchanged."""
        config = {
            "custom_reports": [
                {
                    "name": "simple_report",
                    "level": "ADVERTISER",
                    "granularity": "TOTAL",
                    "columns": ["IMPRESSION_1"],
                }
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 1
        assert result[0]["name"] == "simple_report"
        assert result[0]["level"] == "ADVERTISER"
        assert "engagement_window_days" not in result[0]
        assert "view_window_days" not in result[0]
        assert "click_window_days" not in result[0]

    def test_migration_converts_array_with_zero_value(self):
        """[0] (array containing zero) should be migrated to 0 (integer)."""
        config = {
            "custom_reports": [
                {
                    "name": "test_report",
                    "level": "ADVERTISER",
                    "granularity": "TOTAL",
                    "columns": ["IMPRESSION_1"],
                    "engagement_window_days": [0],
                }
            ]
        }
        result = _evaluate_migration(config)
        assert len(result) == 1
        assert result[0]["engagement_window_days"] == 0


class TestManifestConfigMigrationExists:
    """Tests to verify the config migration is properly defined in the manifest."""

    def test_manifest_has_config_normalization_rules(self):
        """The manifest spec should include config_normalization_rules."""
        manifest_path = Path(__file__).parent.parent / "manifest.yaml"
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)

        assert "config_normalization_rules" in manifest["spec"], "manifest.yaml spec is missing config_normalization_rules"

    def test_manifest_has_window_days_migration(self):
        """The config_normalization_rules should contain a migration for window_days fields."""
        manifest_path = Path(__file__).parent.parent / "manifest.yaml"
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)

        rules = manifest["spec"]["config_normalization_rules"]
        assert rules["type"] == "ConfigNormalizationRules"
        assert "config_migrations" in rules
        assert len(rules["config_migrations"]) >= 1

        migration = rules["config_migrations"][0]
        assert migration["type"] == "ConfigMigration"
        assert "window_days" in migration["description"].lower()

    def test_spec_default_values_are_integers(self):
        """Verify that engagement_window_days and view_window_days have integer defaults, not arrays."""
        manifest_path = Path(__file__).parent.parent / "manifest.yaml"
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)

        custom_report_props = manifest["spec"]["connection_specification"]["properties"]["custom_reports"]["items"]["properties"]

        for field_name in ("click_window_days", "engagement_window_days", "view_window_days"):
            field = custom_report_props[field_name]
            assert field["type"] == "integer", f"{field_name} should have type 'integer'"
            assert isinstance(
                field["default"], int
            ), f"{field_name} default should be an integer, got {type(field['default'])}: {field['default']}"
