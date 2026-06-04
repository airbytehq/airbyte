#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping

import pytest
from source_google_ads.config_migrations import DEPRECATED_FIELDS, MigrateDeprecatedFields
from source_google_ads.source import SourceGoogleAds

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source


CMD = "check"
CONFIG_WITH_DEPRECATED = "unit_tests/test_migrations/deprecated_fields/test_config_with_deprecated.json"
CONFIG_ALREADY_MIGRATED = "unit_tests/test_migrations/deprecated_fields/test_config_already_migrated.json"
SOURCE: Source = SourceGoogleAds({}, None, None)


def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def save_config(config_path: str, config: Mapping[str, Any]) -> None:
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def revert_deprecated_migration(config_path: str) -> None:
    config = load_config(config_path)
    queries = config.get("custom_queries_array", [])
    reverted = []
    for entry in queries:
        new_entry = entry.copy()
        query = entry["query"]
        for old_name, new_name in DEPRECATED_FIELDS.items():
            query = query.replace(new_name, old_name)
        new_entry["query"] = query
        reverted.append(new_entry)
    config["custom_queries_array"] = reverted
    save_config(config_path, config)


@pytest.mark.parametrize(
    "query,expected_query,expected_changed",
    [
        pytest.param(
            "SELECT campaign.name, metrics.video_views FROM campaign",
            "SELECT campaign.name, metrics.video_trueview_views FROM campaign",
            True,
            id="select_video_views",
        ),
        pytest.param(
            "SELECT campaign.name, metrics.video_view_rate FROM campaign",
            "SELECT campaign.name, metrics.video_trueview_view_rate FROM campaign",
            True,
            id="select_video_view_rate",
        ),
        pytest.param(
            "SELECT campaign.name, metrics.average_cpv FROM campaign",
            "SELECT campaign.name, metrics.trueview_average_cpv FROM campaign",
            True,
            id="select_average_cpv",
        ),
        pytest.param(
            "SELECT campaign.name, campaign.start_date FROM campaign",
            "SELECT campaign.name, campaign.start_date_time FROM campaign",
            True,
            id="select_campaign_start_date",
        ),
        pytest.param(
            "SELECT campaign.name, campaign.end_date FROM campaign",
            "SELECT campaign.name, campaign.end_date_time FROM campaign",
            True,
            id="select_campaign_end_date",
        ),
        pytest.param(
            "SELECT campaign.name, metrics.video_views, metrics.video_view_rate FROM campaign",
            "SELECT campaign.name, metrics.video_trueview_views, metrics.video_trueview_view_rate FROM campaign",
            True,
            id="select_both_deprecated",
        ),
        pytest.param(
            "SELECT campaign.name, campaign.start_date, campaign.end_date, metrics.average_cpv FROM campaign",
            "SELECT campaign.name, campaign.start_date_time, campaign.end_date_time, metrics.trueview_average_cpv FROM campaign",
            True,
            id="select_all_three_new_deprecated",
        ),
        pytest.param(
            "SELECT campaign.name, metrics.clicks FROM campaign",
            "SELECT campaign.name, metrics.clicks FROM campaign",
            False,
            id="no_deprecated_fields",
        ),
        pytest.param(
            "SELECT campaign.name, metrics.video_views FROM campaign WHERE metrics.video_views > 0",
            "SELECT campaign.name, metrics.video_trueview_views FROM campaign WHERE metrics.video_trueview_views > 0",
            True,
            id="deprecated_in_select_and_where",
        ),
        pytest.param(
            "SELECT campaign.name, campaign.start_date FROM campaign WHERE campaign.start_date > '2024-01-01'",
            "SELECT campaign.name, campaign.start_date_time FROM campaign WHERE campaign.start_date_time > '2024-01-01'",
            True,
            id="campaign_start_date_in_select_and_where",
        ),
        pytest.param(
            "SELECT campaign.name, metrics.video_views FROM campaign ORDER BY metrics.video_views",
            "SELECT campaign.name, metrics.video_trueview_views FROM campaign ORDER BY metrics.video_trueview_views",
            True,
            id="deprecated_in_select_and_order_by",
        ),
        pytest.param(
            "SELECT campaign.name, campaign.end_date FROM campaign ORDER BY campaign.end_date",
            "SELECT campaign.name, campaign.end_date_time FROM campaign ORDER BY campaign.end_date_time",
            True,
            id="campaign_end_date_in_select_and_order_by",
        ),
        pytest.param(
            "SELECT campaign.name, metrics.video_trueview_views FROM campaign",
            "SELECT campaign.name, metrics.video_trueview_views FROM campaign",
            False,
            id="already_uses_new_field_name",
        ),
    ],
)
def test_replace_fields_in_query(query, expected_query, expected_changed):
    result_query, changed = MigrateDeprecatedFields._replace_fields_in_query(query)
    assert result_query == expected_query
    assert changed == expected_changed


@pytest.mark.parametrize(
    "config,expected",
    [
        pytest.param(
            {"custom_queries_array": [{"query": "SELECT metrics.video_views FROM campaign", "table_name": "t"}]},
            True,
            id="has_deprecated_video_views",
        ),
        pytest.param(
            {"custom_queries_array": [{"query": "SELECT metrics.video_view_rate FROM campaign", "table_name": "t"}]},
            True,
            id="has_deprecated_video_view_rate",
        ),
        pytest.param(
            {"custom_queries_array": [{"query": "SELECT metrics.average_cpv FROM campaign", "table_name": "t"}]},
            True,
            id="has_deprecated_average_cpv",
        ),
        pytest.param(
            {"custom_queries_array": [{"query": "SELECT campaign.start_date FROM campaign", "table_name": "t"}]},
            True,
            id="has_deprecated_campaign_start_date",
        ),
        pytest.param(
            {"custom_queries_array": [{"query": "SELECT campaign.end_date FROM campaign", "table_name": "t"}]},
            True,
            id="has_deprecated_campaign_end_date",
        ),
        pytest.param(
            {"custom_queries_array": [{"query": "SELECT metrics.clicks FROM campaign", "table_name": "t"}]},
            False,
            id="no_deprecated_fields",
        ),
        pytest.param(
            {
                "custom_queries_array": [
                    {"query": "SELECT campaign.start_date_time, campaign.end_date_time FROM campaign", "table_name": "t"}
                ]
            },
            False,
            id="already_uses_new_date_time_fields",
        ),
        pytest.param(
            {"custom_queries_array": []},
            False,
            id="empty_queries",
        ),
        pytest.param(
            {},
            False,
            id="no_custom_queries_array",
        ),
    ],
)
def test_should_migrate(config, expected):
    assert MigrateDeprecatedFields.should_migrate(config) == expected


def test_update_custom_queries():
    config = {
        "custom_queries_array": [
            {
                "query": "SELECT campaign.name, metrics.video_views, metrics.video_view_rate, metrics.average_cpv FROM campaign",
                "table_name": "ad_stats",
                "primary_key": None,
            },
            {
                "query": "SELECT ad_group.name, metrics.impressions FROM ad_group",
                "table_name": "clean_query",
                "primary_key": None,
            },
            {
                "query": "SELECT campaign.name, campaign.start_date, campaign.end_date FROM campaign",
                "table_name": "campaign_dates",
                "primary_key": None,
            },
        ]
    }
    result = MigrateDeprecatedFields.update_custom_queries(config)
    # First query: all three metric fields migrated
    assert "metrics.video_trueview_views" in result["custom_queries_array"][0]["query"]
    assert "metrics.video_trueview_view_rate" in result["custom_queries_array"][0]["query"]
    assert "metrics.trueview_average_cpv" in result["custom_queries_array"][0]["query"]
    assert "metrics.video_views" not in result["custom_queries_array"][0]["query"]
    assert "metrics.video_view_rate" not in result["custom_queries_array"][0]["query"]
    assert "metrics.average_cpv" not in result["custom_queries_array"][0]["query"]
    # Second query should be unchanged
    assert result["custom_queries_array"][1]["query"] == "SELECT ad_group.name, metrics.impressions FROM ad_group"
    # Third query: campaign date fields migrated
    assert "campaign.start_date_time" in result["custom_queries_array"][2]["query"]
    assert "campaign.end_date_time" in result["custom_queries_array"][2]["query"]
    assert "campaign.start_date," not in result["custom_queries_array"][2]["query"]
    assert "campaign.end_date " not in result["custom_queries_array"][2]["query"]


def test_migrate_config_end_to_end(capsys):
    args = [CMD, "--config", CONFIG_WITH_DEPRECATED]
    original_config = load_config(CONFIG_WITH_DEPRECATED)
    assert MigrateDeprecatedFields.should_migrate(original_config)

    MigrateDeprecatedFields.migrate(args, SOURCE)

    migrated_config = load_config(CONFIG_WITH_DEPRECATED)

    # Deprecated metric fields should be replaced
    ad_stats_query = migrated_config["custom_queries_array"][0]["query"]
    assert "metrics.video_trueview_views" in ad_stats_query
    assert "metrics.video_trueview_view_rate" in ad_stats_query
    assert "metrics.trueview_average_cpv" in ad_stats_query
    assert "metrics.video_views" not in ad_stats_query
    assert "metrics.average_cpv" not in ad_stats_query

    # Clean query should be unchanged
    assert migrated_config["custom_queries_array"][1]["query"] == "SELECT ad_group.name, metrics.impressions FROM ad_group"

    # Campaign date fields should be replaced
    campaign_dates_query = migrated_config["custom_queries_array"][2]["query"]
    assert "campaign.start_date_time" in campaign_dates_query
    assert "campaign.end_date_time" in campaign_dates_query

    # Migration should now be a no-op
    assert not MigrateDeprecatedFields.should_migrate(migrated_config)

    # CONTROL MESSAGE was emitted
    captured = capsys.readouterr().out
    control_msg = json.loads(captured)
    assert control_msg["type"] == Type.CONTROL.value
    assert control_msg["control"]["type"] == OrchestratorType.CONNECTOR_CONFIG.value

    # Revert to original state for test idempotency
    revert_deprecated_migration(CONFIG_WITH_DEPRECATED)


def test_migrate_skips_already_migrated_config(capsys):
    args = [CMD, "--config", CONFIG_ALREADY_MIGRATED]
    original_config = load_config(CONFIG_ALREADY_MIGRATED)
    assert not MigrateDeprecatedFields.should_migrate(original_config)

    MigrateDeprecatedFields.migrate(args, SOURCE)

    # No CONTROL message should have been emitted
    captured = capsys.readouterr().out
    assert captured == ""

    # Config should be unchanged
    after_config = load_config(CONFIG_ALREADY_MIGRATED)
    assert after_config == original_config


def test_config_reverted_after_migration():
    config = load_config(CONFIG_WITH_DEPRECATED)
    assert "metrics.video_views" in config["custom_queries_array"][0]["query"]
    assert "metrics.video_view_rate" in config["custom_queries_array"][0]["query"]
    assert "metrics.average_cpv" in config["custom_queries_array"][0]["query"]
    assert "campaign.start_date" in config["custom_queries_array"][2]["query"]
    assert "campaign.end_date" in config["custom_queries_array"][2]["query"]


def test_unparseable_query_is_skipped():
    config = {
        "custom_queries_array": [
            {
                "query": "THIS IS NOT A VALID GAQL QUERY metrics.video_views",
                "table_name": "bad_query",
                "primary_key": None,
            },
        ]
    }
    result = MigrateDeprecatedFields.update_custom_queries(config)
    # Unparseable query should be kept as-is
    assert result["custom_queries_array"][0]["query"] == "THIS IS NOT A VALID GAQL QUERY metrics.video_views"
