# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Tests for the pixel_events_statistics stream to verify that the pixel_ids
parameter is sent as a JSON array in the request URL.

This test validates the fix for the bug where pixel_ids was being sent as
a plain string instead of a JSON array, causing the TikTok API to return
error code 40002: "pixel_ids: Field must be set to array".

See: https://github.com/airbytehq/oncall/issues/10291
Fix PR: https://github.com/airbytehq/airbyte/pull/70241
"""

from pathlib import Path

import pytest
import yaml
from jinja2 import Environment


def get_manifest_path() -> Path:
    return Path(__file__).parent.parent.parent / "manifest.yaml"


def load_manifest() -> dict:
    with open(get_manifest_path(), "r") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "pixel_id,expected_pixel_ids_param",
    [
        pytest.param(
            "7577353199770828808",
            '["7577353199770828808"]',
            id="single_pixel_id_as_json_array",
        ),
        pytest.param(
            "1234567890123456789",
            '["1234567890123456789"]',
            id="another_pixel_id_as_json_array",
        ),
    ],
)
def test_pixel_ids_request_parameter_format(pixel_id: str, expected_pixel_ids_param: str):
    """
    Test that the pixel_ids request parameter in the manifest.yaml is configured
    to produce a JSON array string format.

    The TikTok API requires pixel_ids to be a JSON array like '["7577353199770828808"]',
    not a plain string like '7577353199770828808'.

    This test verifies the manifest.yaml configuration produces the correct format
    when the Jinja template is rendered with a pixel_id from the stream partition.
    """
    manifest = load_manifest()

    pixel_events_statistics_def = manifest["definitions"]["pixel_events_statistics"]
    request_parameters = pixel_events_statistics_def["retriever"]["requester"]["request_parameters"]
    pixel_ids_template = request_parameters["pixel_ids"]

    env = Environment()
    template = env.from_string(pixel_ids_template)
    rendered_pixel_ids = template.render(stream_partition={"pixel_id": pixel_id})

    assert rendered_pixel_ids == expected_pixel_ids_param, (
        f"pixel_ids should be rendered as a JSON array string. "
        f"Expected: {expected_pixel_ids_param}, Got: {rendered_pixel_ids}"
    )


def test_pixel_events_statistics_stream_exists():
    """
    Test that the pixel_events_statistics stream is defined in the manifest.
    """
    manifest = load_manifest()
    assert "pixel_events_statistics" in manifest["definitions"]


def test_pixel_events_statistics_uses_correct_endpoint():
    """
    Test that the pixel_events_statistics stream uses the correct API endpoint.
    """
    manifest = load_manifest()
    pixel_events_statistics_def = manifest["definitions"]["pixel_events_statistics"]
    path = pixel_events_statistics_def["retriever"]["requester"]["path"]
    assert path == "pixel/event/stats/"


def test_pixel_events_statistics_has_required_request_parameters():
    """
    Test that the pixel_events_statistics stream has the required request parameters.
    """
    manifest = load_manifest()
    pixel_events_statistics_def = manifest["definitions"]["pixel_events_statistics"]
    request_parameters = pixel_events_statistics_def["retriever"]["requester"]["request_parameters"]

    assert "pixel_ids" in request_parameters, "pixel_ids parameter is required"
    assert "date_range" in request_parameters, "date_range parameter is required"
