#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Test that the manifest path parameter is empty, preventing a trailing slash
from being appended to the configured RSS feed URL.

When path was set to "/" the CDK would append a trailing "/" to the base URL,
which corrupts URLs that contain query parameters. For example:
  https://example.com/feed/?key=test123  ->  https://example.com/feed/?key=test123/
Setting path to "" avoids the issue entirely.
"""

from pathlib import Path

import yaml


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "source_rss" / "manifest.yaml"


def _load_manifest() -> dict:
    with open(MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


def test_items_stream_path_is_empty_string():
    """The items stream $parameters.path must be '' (empty string), not '/'."""
    manifest = _load_manifest()
    items_stream = manifest["definitions"]["items_stream"]
    path_value = items_stream["$parameters"]["path"]
    assert path_value == "", (
        f"Expected items_stream path to be an empty string, got {path_value!r}. "
        "A non-empty path (especially '/') causes the CDK to append a trailing slash "
        "to the base URL, which breaks URLs with query parameters."
    )


def test_url_base_uses_config_url_without_extra_path():
    """
    Verify that the requester url_base is the raw config URL and the path
    parameter does not inject any additional path segment.
    """
    manifest = _load_manifest()
    requester = manifest["definitions"]["requester"]
    assert requester["url_base"] == "{{ config['url'] }}"
    items_stream = manifest["definitions"]["items_stream"]
    # The effective request URL should be url_base + path.
    # With path == "", the final URL equals the configured URL exactly.
    assert items_stream["$parameters"]["path"] == ""
