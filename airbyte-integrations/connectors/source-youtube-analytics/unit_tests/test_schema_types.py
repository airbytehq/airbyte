#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Report metrics follow YouTube's definitions (counts integer, ratios/percentages number): https://developers.google.com/youtube/reporting/v1/reports/metrics. See airbytehq/airbyte-internal-issues#18052."""

import logging

import pytest
from _helpers import get_source


EXPECTED_REPORT_METRIC_TYPES = {
    "channel_annotations_a1": {
        "annotation_click_through_rate": "number",
        "annotation_close_rate": "number",
        "annotation_clickable_impressions": "integer",
        "annotation_clicks": "integer",
        "annotation_closable_impressions": "integer",
        "annotation_closes": "integer",
        "annotation_impressions": "integer",
    },
    "channel_cards_a1": {
        "card_click_rate": "number",
        "card_teaser_click_rate": "number",
        "card_clicks": "integer",
        "card_impressions": "integer",
        "card_teaser_clicks": "integer",
        "card_teaser_impressions": "integer",
    },
    "channel_demographics_a1": {"views_percentage": "number"},
    "channel_end_screens_a1": {
        "end_screen_element_click_rate": "number",
        "end_screen_element_clicks": "integer",
        "end_screen_element_impressions": "integer",
    },
    "channel_sharing_service_a1": {"shares": "integer"},
    "channel_province_a3": {
        "annotation_click_through_rate": "number",
        "annotation_close_rate": "number",
        "card_click_rate": "number",
        "card_teaser_click_rate": "number",
    },
    "playlist_province_a2": {
        "playlist_saves_added": "integer",
        "playlist_saves_removed": "integer",
        "playlist_starts": "integer",
        "views": "integer",
    },
}


@pytest.mark.parametrize(
    ("stream_name", "field", "expected_type"),
    [
        (stream_name, field, expected_type)
        for stream_name, fields in EXPECTED_REPORT_METRIC_TYPES.items()
        for field, expected_type in fields.items()
    ],
)
def test_report_metric_types_match_vendor(config, stream_name, field, expected_type):
    """Every corrected report metric has its vendor-defined JSON Schema type."""
    source = get_source(config)
    streams = {stream.name: stream for stream in source.discover(logging.getLogger("test"), config).streams}

    assert streams[stream_name].json_schema["properties"][field]["type"] == ["null", expected_type]


def test_shared_metric_fields_have_consistent_types_across_report_streams(config):
    """Shared non-key report fields use the same type in every stream."""
    source = get_source(config)
    catalog = source.discover(logging.getLogger("test"), config)
    types_by_field = {}

    for stream in catalog.streams:
        if stream.name == "report_types":
            continue
        primary_key_fields = {field for key in stream.source_defined_primary_key for field in key}
        for field, schema in stream.json_schema.get("properties", {}).items():
            if field == "date" or field in primary_key_fields:
                continue
            types_by_field.setdefault(field, {})[stream.name] = schema.get("type")

    for field, stream_types in types_by_field.items():
        if len(stream_types) < 2:
            continue
        declared_types = list(stream_types.values())
        assert all(
            field_type == declared_types[0] for field_type in declared_types[1:]
        ), f"Field {field!r} has inconsistent types across report streams: {stream_types}"
