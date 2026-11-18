# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml
from freezegun import freeze_time

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"
_YESTERDAY = "(now_utc() - duration('P1D')).strftime('%Y-%m-%dT23:59:59Z')"
# The optional end_date bounds only the report streams: their last window stops at the end of that
# day, or at the end of yesterday when that is earlier, and they behave as before when it is unset.
_REPORT_END_TEMPLATE = (
    "{{ [config['end_date'][:10] ~ 'T23:59:59Z', " + _YESTERDAY + "] | min "
    "if config.get('end_date') else " + _YESTERDAY + " }}"
)
_REPORT_STREAMS = {"flow_series_reports", "campaign_values_reports"}


def _manifest():
    return yaml.safe_load(_MANIFEST_PATH.read_text())


def _end_datetime_templates(node):
    templates = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "end_datetime":
                templates.append(value["datetime"] if isinstance(value, dict) else value)
            templates.extend(_end_datetime_templates(value))
    elif isinstance(node, list):
        for item in node:
            templates.extend(_end_datetime_templates(item))
    return templates


def test_report_streams_use_the_bounded_end_datetime():
    streams = _manifest()["definitions"]["streams"]
    for name in sorted(_REPORT_STREAMS):
        assert _end_datetime_templates(streams[name]) == [_REPORT_END_TEMPLATE], name


def test_no_other_stream_reads_end_date():
    streams = _manifest()["definitions"]["streams"]
    for name, stream in streams.items():
        if name not in _REPORT_STREAMS:
            assert "end_date" not in yaml.safe_dump(stream), name


def test_end_date_is_an_optional_date():
    spec = _manifest()["spec"]["connection_specification"]
    assert "end_date" not in spec.get("required", [])
    prop = spec["properties"]["end_date"]
    assert prop["type"] == "string"
    assert prop["pattern"] == r"^\d{4}-\d{2}-\d{2}$"


@freeze_time("2024-06-15T12:00:00Z")
def test_unset_end_date_ends_yesterday():
    interpolation = JinjaInterpolation()
    assert interpolation.eval(_REPORT_END_TEMPLATE, config={}) == "2024-06-14T23:59:59Z"
    assert interpolation.eval(_REPORT_END_TEMPLATE, config={"end_date": ""}) == "2024-06-14T23:59:59Z"


@freeze_time("2024-06-15T12:00:00Z")
def test_past_end_date_ends_at_the_end_of_that_day():
    assert JinjaInterpolation().eval(_REPORT_END_TEMPLATE, config={"end_date": "2023-12-31"}) == "2023-12-31T23:59:59Z"


@freeze_time("2024-06-15T12:00:00Z")
def test_end_date_today_or_later_still_ends_yesterday():
    interpolation = JinjaInterpolation()
    assert interpolation.eval(_REPORT_END_TEMPLATE, config={"end_date": "2024-06-15"}) == "2024-06-14T23:59:59Z"
    assert interpolation.eval(_REPORT_END_TEMPLATE, config={"end_date": "2030-01-01"}) == "2024-06-14T23:59:59Z"
