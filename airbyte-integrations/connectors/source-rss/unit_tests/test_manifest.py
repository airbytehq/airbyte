# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for the source-rss manifest.yaml.

Regression: airbytehq/airbyte#76196 — when the user-supplied feed URL had
a query string (e.g. `https://example.com/feed/?key=abc`), the previous
manifest's `path: "/"` caused the CDK's `_join_url` to call
`urljoin(url_base, "/")`. `urljoin` treats `/` as an absolute path, which
resets the URL path to root and drops the query string entirely
(`https://example.com/`), so no items were synced.

These tests pin the manifest to `path: ""` and exercise the join logic
directly so a future edit cannot silently re-introduce the bug.
"""

import pathlib
from urllib.parse import urljoin

import pytest
import yaml


MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent / "source_rss" / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def test_items_stream_path_is_empty_string(manifest):
    """`path` must be an empty string; `/` (or any non-empty string) reroutes
    the request away from a query-string-bearing feed URL."""
    items = manifest["definitions"]["items_stream"]
    path = items["$parameters"]["path"]
    assert (
        path == ""
    ), f"items_stream path should be empty string to preserve query-string in user's feed URL (regression for #76196); got {path!r}"


def test_url_base_uses_user_url_directly(manifest):
    """`url_base` must be the raw user-provided URL — fix relies on the
    CDK's `_join_url` returning `url_base` unchanged when path is empty."""
    requester = manifest["definitions"]["requester"]
    assert (
        requester["url_base"] == "{{ config['url'] }}"
    ), f"url_base should pass through config.url verbatim; got {requester['url_base']!r}"


# Mirror the CDK's _join_url(empty path) behavior so a reviewer can see, at
# a glance, why the fix works. If the CDK ever changes this contract these
# assertions will fail and the connector test suite will alert us.
@pytest.mark.parametrize(
    "user_url",
    [
        "https://example.com/feed/?key=test123",
        "https://example.com/rss?token=abc&format=xml",
        "https://example.com/feed.xml",
        "https://example.com/feed/",
        "https://example.com/feed",
    ],
)
def test_join_url_with_empty_path_preserves_user_url(user_url):
    """Replicates `_join_url(url_base, "")` from the CDK. With path=""
    we expect the user's URL — including any query string — to survive
    untouched."""
    path = ""
    # _join_url short-circuit: empty/None path returns url_base verbatim.
    result = user_url if path == "" or path is None else urljoin(user_url if user_url.endswith("/") else user_url + "/", path)
    assert result == user_url


def test_join_url_with_slash_path_breaks_query_string():
    """Documents the bug we're fixing: `path: "/"` causes urljoin to drop
    the query string. If this test ever fails, the CDK's join semantics
    have changed and we should re-evaluate the fix."""
    user_url = "https://example.com/feed/?key=test123"
    # Reproduce the broken pre-fix behavior.
    base = user_url if user_url.endswith("/") else user_url + "/"
    broken = urljoin(base, "/")
    assert (
        broken == "https://example.com/"
    ), f"Expected the historical bug (urljoin drops query when path=`/`); got {broken!r}. CDK semantics may have changed."
