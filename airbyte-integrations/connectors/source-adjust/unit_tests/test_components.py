#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from source_adjust.source import SourceAdjust


def get_report_schema(config):
    source = SourceAdjust(config=config, catalog=None, state=None)
    stream = next(stream for stream in source.streams(config) if stream.name == "AdjustReport")
    return stream.get_json_schema()


def test_report_schema_matches_pydantic_v1_shape(config_pass):
    config = {**config_pass, "additional_metrics": ["custom_metric"]}

    assert get_report_schema(config) == {
        "title": "Report",
        "type": "object",
        "properties": {
            "network_cost": {
                "title": "Network Cost",
                "description": "Ad Spend (Network).",
                "type": "number",
            },
            "network_installs": {
                "title": "Network Installs",
                "description": "Installs (Network).",
                "type": "integer",
            },
            "network_ecpi": {
                "title": "Network Ecpi",
                "description": "eCPI (Network).",
                "type": "number",
            },
            "installs": {
                "title": "Installs",
                "description": "Installs.",
                "type": "integer",
            },
            "day": {
                "title": "Day",
                "description": "Date.",
                "type": "string",
                "format": "date",
            },
            "app": {
                "title": "App",
                "description": "Name of the app.",
                "type": "string",
            },
            "campaign": {
                "title": "Campaign",
                "description": "Tracker sub-level 1. String value usually contains campaign name and id.",
                "type": "string",
            },
            "campaign_network": {
                "title": "Campaign Network",
                "description": "Campaign name from the network.",
                "type": "string",
            },
            "campaign_id_network": {
                "title": "Campaign Id Network",
                "description": "Campaign ID from the network.",
                "type": "string",
            },
            "partner_name": {
                "title": "Partner Name",
                "description": "Partner's name in the Adjust system.",
                "type": "string",
            },
            "custom_metric": {"type": "number"},
        },
        "required": ["day"],
        "$schema": "http://json-schema.org/draft-07/schema#",
    }


def test_report_schema_has_no_nullable_unions():
    config = {
        "ingest_start": "2024-05-20T20:30:40Z",
        "api_token": "token",
        "metrics": [
            "network_cost",
            "network_cost_diff",
            "network_clicks",
            "network_impressions",
            "network_installs",
            "network_installs_diff",
            "network_ecpc",
            "network_ecpi",
            "network_ecpm",
            "arpdau_ad",
            "arpdau",
            "arpdau_iap",
            "ad_impressions",
            "ad_rpm",
            "ad_revenue",
            "cohort_ad_revenue",
            "cost",
            "adjust_cost",
            "all_revenue",
            "cohort_all_revenue",
            "daus",
            "maus",
            "waus",
            "base_sessions",
            "ctr",
            "click_conversion_rate",
            "click_cost",
            "clicks",
            "paid_clicks",
            "deattributions",
            "ecpc",
            "gdpr_forgets",
            "gross_profit",
            "cohort_gross_profit",
            "impression_conversion_rate",
            "impression_cost",
            "impressions",
            "paid_impressions",
            "install_cost",
            "installs",
            "paid_installs",
            "installs_per_mile",
            "limit_ad_tracking_installs",
            "limit_ad_tracking_install_rate",
            "limit_ad_tracking_reattribution_rate",
            "limit_ad_tracking_reattributions",
            "non_organic_installs",
            "organic_installs",
            "roas_ad",
            "roas",
            "roas_iap",
            "reattributions",
            "return_on_investment",
            "revenue",
            "cohort_revenue",
            "revenue_events",
            "revenue_to_cost",
            "sessions",
            "events",
            "ecpi_all",
            "ecpi",
            "ecpm",
        ],
        "dimensions": [
            "os_name",
            "device_type",
            "app",
            "app_token",
            "store_id",
            "store_type",
            "app_network",
            "currency",
            "currency_code",
            "network",
            "campaign",
            "campaign_network",
            "campaign_id_network",
            "adgroup",
            "adgroup_network",
            "adgroup_id_network",
            "source_network",
            "source_id_network",
            "creative",
            "creative_network",
            "creative_id_network",
            "country",
            "country_code",
            "region",
            "partner_name",
            "partner_id",
        ],
        "additional_metrics": ["custom_metric_x"],
        "until_today": True,
    }
    schema = get_report_schema(config)
    properties = schema["properties"]

    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert all("type" in property_schema for property_schema in properties.values())
    assert all("anyOf" not in property_schema and "default" not in property_schema for property_schema in properties.values())
