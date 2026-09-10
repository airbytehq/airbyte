#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Website / App / Shop conversion metrics on the daily report streams.

TikTok reports each conversion event separately per channel (Website pixel, App MMP, Shop)
and exposes no cross-channel roll-up metric, so a single "adds to cart" or "content views"
figure requires all three legs. These tests pin the metric lists so a leg cannot be dropped
without a failing test.
"""

import yaml

import pytest

from .conftest import _YAML_FILE_PATH


# The Website / App / Shop legs, added to every daily report stream.
FUNNEL_LEGS = [
    "web_event_add_to_cart",
    "page_content_view_events",
    "onsite_on_web_cart",
    "onsite_on_web_detail",
    "total_view_content",
    "total_purchase",
    "total_sales_lead_value",
]

# Purchase counts and values, added at ad group and campaign level.
PURCHASE_METRICS = [
    "complete_payment",
    "total_complete_payment_rate",
    "onsite_shopping",
    "total_onsite_shopping_value",
    "total_app_event_add_to_cart",
    "total_purchase_value",
]

# Generic conversion metrics, added at campaign level.
CONVERSION_METRICS = [
    "conversion",
    "conversion_rate",
    "cost_per_conversion",
    "real_time_conversion",
]

EXPECTED = {
    "ads_reports_daily": FUNNEL_LEGS,
    "ad_groups_reports_daily": FUNNEL_LEGS + PURCHASE_METRICS,
    "campaigns_reports_daily": FUNNEL_LEGS + PURCHASE_METRICS + CONVERSION_METRICS,
}

# report_type=AUDIENCE rejects these metrics, so the audience streams must not carry them.
AUDIENCE_STREAMS = [
    "ads_audience_reports_daily",
    "ad_group_audience_reports_daily",
    "campaigns_audience_reports_daily",
]


@pytest.fixture(scope="module")
def manifest():
    with open(_YAML_FILE_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _report_metrics(manifest, stream_name):
    definition = manifest["definitions"][f"{stream_name}_stream"]
    return definition["$parameters"]["report_metrics"]


@pytest.mark.parametrize("stream_name, expected_metrics", EXPECTED.items(), ids=list(EXPECTED))
def test_daily_report_streams_request_conversion_metrics(manifest, stream_name, expected_metrics):
    metrics = _report_metrics(manifest, stream_name)
    missing = [metric for metric in expected_metrics if metric not in metrics]
    assert not missing, f"{stream_name} is missing conversion metrics: {missing}"


@pytest.mark.parametrize("stream_name", list(EXPECTED), ids=list(EXPECTED))
def test_daily_report_streams_have_no_duplicate_metrics(manifest, stream_name):
    metrics = _report_metrics(manifest, stream_name)
    duplicates = {metric for metric in metrics if metrics.count(metric) > 1}
    assert not duplicates, f"{stream_name} requests duplicate metrics: {sorted(duplicates)}"


@pytest.mark.parametrize("stream_name", AUDIENCE_STREAMS, ids=AUDIENCE_STREAMS)
def test_audience_streams_do_not_request_conversion_metrics(manifest, stream_name):
    """report_type=AUDIENCE rejects these metrics; requesting one fails the whole call."""
    metrics = _report_metrics(manifest, stream_name)
    leaked = [metric for metric in FUNNEL_LEGS + PURCHASE_METRICS if metric in metrics]
    assert not leaked, f"{stream_name} must not request BASIC-only metrics: {leaked}"


@pytest.mark.parametrize("metric", FUNNEL_LEGS, ids=FUNNEL_LEGS)
def test_new_metrics_are_declared_in_base_report_schema(manifest, metric):
    properties = manifest["definitions"]["schemas"]["base_report"]["properties"]["metrics"]["properties"]
    assert metric in properties, f"{metric} is requested but not declared in the base_report schema"


def test_deprecated_content_view_metric_is_not_requested_alongside_its_replacement(manifest):
    """`page_content_view_events` and `product_details_page_browse` are the same event.

    They return identical values, so requesting both would invite double counting downstream.
    """
    for stream_name in EXPECTED:
        metrics = _report_metrics(manifest, stream_name)
        assert not (
            "page_content_view_events" in metrics and "product_details_page_browse" in metrics
        ), f"{stream_name} requests both the deprecated and current content-view metric"
