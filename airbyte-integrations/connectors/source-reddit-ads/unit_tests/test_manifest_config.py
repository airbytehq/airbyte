# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import timedelta

import requests
import yaml
from conftest import _MANIFEST_PATH, base_config, get_source

from airbyte_cdk.sources.declarative.models.declarative_component_schema import ConcurrencyLevel, HttpRequestRegexMatcher, Rate
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver


def _runtime_matcher(source, manifest_matcher: dict):
    return source._constructor.create_component(
        HttpRequestRegexMatcher,
        manifest_matcher,
        source._config,
    )


def test_api_budget_resolves_separate_campaign_and_report_policies() -> None:
    source = get_source()
    policies = source.resolved_manifest["api_budget"]["policies"]

    assert len(policies) == 2
    limits = []
    matches = []
    for policy in policies:
        rate = source._constructor.create_component(
            Rate,
            {**policy["rates"][0], "type": "Rate"},
            source._config,
        )
        limits.append((rate.limit, rate.interval))
        matches.append([_runtime_matcher(source, matcher) for matcher in policy["matchers"]])

    assert limits == [(400, timedelta(minutes=1)), (60, timedelta(minutes=1))]
    requests_by_path = {
        "/api/v3/ad_accounts/a2_abc123": requests.Request("GET", "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123").prepare(),
        "/api/v3/ad_accounts/a2_abc123/ad_groups": requests.Request(
            "GET", "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123/ad_groups"
        ).prepare(),
        "/api/v3/ad_accounts/a2_abc123/ads": requests.Request(
            "GET", "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123/ads"
        ).prepare(),
        "/api/v3/ad_accounts/a2_abc123/campaigns": requests.Request(
            "GET", "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123/campaigns"
        ).prepare(),
        "/api/v3/ad_accounts/a2_abc123/reports": requests.Request(
            "POST", "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123/reports"
        ).prepare(),
    }
    matched = {
        path: [index for index, policy_matchers in enumerate(matches) if any(matcher(request) for matcher in policy_matchers)]
        for path, request in requests_by_path.items()
    }

    assert matched == {
        "/api/v3/ad_accounts/a2_abc123": [0],
        "/api/v3/ad_accounts/a2_abc123/ad_groups": [0],
        "/api/v3/ad_accounts/a2_abc123/ads": [0],
        "/api/v3/ad_accounts/a2_abc123/campaigns": [0],
        "/api/v3/ad_accounts/a2_abc123/reports": [1],
    }
    assert source.resolved_manifest["api_budget"]["status_codes_for_ratelimit_hit"] == [429]


def test_rate_limit_and_retry_filters_precede_ad_account_classification() -> None:
    source = get_source()
    campaign_report = next(stream for stream in source.resolved_manifest["streams"] if stream["name"] == "campaign_report")
    error_handlers = [
        source.resolved_manifest["definitions"]["linked"]["HttpRequester"]["error_handler"],
        campaign_report["retriever"]["requester"]["error_handler"],
    ]
    ad_account_filter = source.resolved_manifest["definitions"]["linked"]["BadAdAccount400Filter"]

    for error_handler in error_handlers:
        response_filters = error_handler["response_filters"]
        assert response_filters[1]["action"] == "RATE_LIMITED"
        assert response_filters[1]["http_codes"] == [429]
        assert response_filters[2]["action"] == "RETRY"
        assert response_filters[2]["http_codes"] == [500, 502, 503, 504]
        ad_account_filter_index = next(
            index for index, response_filter in enumerate(response_filters) if response_filter == ad_account_filter
        )
        assert ad_account_filter_index > 2


def test_concurrency_resolves_default_configured_and_clamped_values() -> None:
    expected = [
        ({}, 3),
        ({"num_workers": 7}, 7),
        ({"num_workers": 20}, 10),
        ({"num_workers": 0}, 3),
        ({"num_workers": True}, 3),
    ]

    for overrides, expected_workers in expected:
        source = get_source(base_config(**overrides))
        concurrency = source._constructor.create_component(
            ConcurrencyLevel,
            source.resolved_manifest["concurrency_level"],
            source._config,
        )
        assert concurrency.get_concurrency_level() == expected_workers


def test_spec_fields_are_human_readable_and_keep_sensitive_fields_secret() -> None:
    source = get_source()
    properties = source.resolved_manifest["spec"]["connection_specification"]["properties"]

    assert properties["ad_account_id"]["title"] == "Ad Account ID"
    assert "shown in Reddit Ads Manager" in properties["ad_account_id"]["description"]
    assert properties["start_time"]["title"] == "Start Date"
    assert properties["ad_account_id"]["airbyte_secret"] is True
    assert properties["user_agent"]["title"] == "User Agent"
    assert properties["user_agent"]["airbyte_secret"] is True
    assert properties["num_workers"]["title"] == "Number of Concurrent Workers"
    assert properties["num_workers"]["type"] == "integer"
    assert properties["num_workers"]["order"] == 6
    assert properties["num_workers"]["default"] == 3
    assert properties["num_workers"]["minimum"] == 1
    assert properties["num_workers"]["maximum"] == 10
    assert "num_workers" not in source.resolved_manifest["spec"]["connection_specification"]["required"]


def test_report_lookback_window_spec_is_optional_and_bounded() -> None:
    source = get_source()
    connection_specification = source.resolved_manifest["spec"]["connection_specification"]
    field = connection_specification["properties"]["report_lookback_window_days"]

    assert field["title"] == "Report Lookback Window (Days)"
    assert field["default"] == 7
    assert field["minimum"] == 0
    assert field["maximum"] == 30
    assert "report_lookback_window_days" not in connection_specification["required"]


def test_report_schemas_resolve_without_yaml_merge_keys() -> None:
    # yaml.BaseLoader ignores YAML merge keys, like the platform's Jackson parser when the connector is forked in the Connector Builder.
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.load(_MANIFEST_PATH.read_text(), Loader=yaml.BaseLoader))
    report_streams = [stream for stream in manifest["streams"] if stream["name"].endswith("_report")]

    assert len(report_streams) == 4
    for stream in report_streams:
        assert {"impressions", "spend"} <= stream["schema_loader"]["schema"]["properties"].keys(), stream["name"]
