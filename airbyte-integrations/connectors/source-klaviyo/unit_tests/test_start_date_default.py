# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml
from freezegun import freeze_time

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"
_EXPECTED_TEMPLATE = "{{ config.get('start_date', (now_utc() - duration('P1Y')).strftime('%Y-%m-%dT%H:%M:%SZ')) }}"
# The report streams take the same start date but floor it to midnight, because Klaviyo report
# timeframes are inclusive on both ends: a window that stops mid-day reports that day and so does
# the next window, which double-counts it. Klaviyo reads the bound in the account's company
# timezone and ignores the offset written here.
_REPORT_TEMPLATE = "{{ config.get('start_date', (now_utc() - duration('P1Y')).strftime('%Y-%m-%dT%H:%M:%SZ'))[:10] }}T00:00:00Z"
_REPORT_STREAMS = {"flow_series_reports", "campaign_values_reports"}
# The metrics stream ignores start_date so that every metric definition is synced and can be
# joined against events (https://github.com/airbytehq/airbyte/pull/61338).
_METRICS_EXPECTED_START = "1970-01-01T00:00:00Z"


def _collect_start_datetime_templates(node):
    templates = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "start_datetime":
                if isinstance(value, str):
                    templates.append(value)
                elif isinstance(value, dict) and isinstance(value.get("datetime"), str):
                    templates.append(value["datetime"])
            templates.extend(_collect_start_datetime_templates(value))
    elif isinstance(node, list):
        for item in node:
            templates.extend(_collect_start_datetime_templates(item))
    return templates


def test_manifest_uses_one_year_default_for_every_stream():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    streams = manifest["definitions"]["streams"]
    metrics_templates = _collect_start_datetime_templates(streams.pop("metrics"))
    report_templates = [template for name in sorted(_REPORT_STREAMS) for template in _collect_start_datetime_templates(streams.pop(name))]
    templates = _collect_start_datetime_templates(streams)

    assert templates, "Expected to find start_datetime templates in the manifest"
    assert all(template == _EXPECTED_TEMPLATE for template in templates)
    assert report_templates == [_REPORT_TEMPLATE] * len(_REPORT_STREAMS)
    assert metrics_templates == [_METRICS_EXPECTED_START]


@freeze_time("2024-06-15T12:00:00Z")
def test_blank_start_date_defaults_to_one_year_back():
    result = JinjaInterpolation().eval(_EXPECTED_TEMPLATE, config={})
    assert result == "2023-06-15T12:00:00Z"


@freeze_time("2024-06-15T12:00:00Z")
def test_configured_start_date_is_left_unchanged():
    result = JinjaInterpolation().eval(_EXPECTED_TEMPLATE, config={"start_date": "2020-01-01T00:00:00Z"})
    assert result == "2020-01-01T00:00:00Z"


@freeze_time("2024-06-15T12:00:00Z")
def test_report_streams_floor_the_start_date_to_midnight():
    """The report streams keep the same start date, only moved back to the start of its day."""
    interpolation = JinjaInterpolation()

    assert interpolation.eval(_REPORT_TEMPLATE, config={}) == "2023-06-15T00:00:00Z"
    assert interpolation.eval(_REPORT_TEMPLATE, config={"start_date": "2020-01-01T09:30:45Z"}) == "2020-01-01T00:00:00Z"
    assert interpolation.eval(_REPORT_TEMPLATE, config={"start_date": "2020-01-01T00:00:00Z"}) == "2020-01-01T00:00:00Z"
