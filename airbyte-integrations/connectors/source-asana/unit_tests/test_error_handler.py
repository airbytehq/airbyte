#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_asana.source import SourceAsana

from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


def _load_manifest():
    source = SourceAsana(catalog=None, config=None, state=None)
    return source._source_config


@pytest.mark.parametrize(
    "status_code,json_body,expected_action",
    [
        pytest.param(
            400,
            {
                "errors": [
                    {
                        "message": (
                            "There is currently an upper limit on the number of results "
                            "returned for this query. Please see docs at "
                            "https://developers.asana.com/docs/api-limits. "
                            "We apologize for any inconvenience this has caused."
                        )
                    }
                ]
            },
            ResponseAction.IGNORE,
            id="pagination_limit_error_is_ignored",
        ),
        pytest.param(
            400,
            {"errors": [{"message": "Some other bad request error."}]},
            ResponseAction.FAIL,
            id="generic_400_error_still_fails",
        ),
    ],
)
def test_pagination_limit_error_handler(status_code, json_body, expected_action):
    """Verify the error handler ignores Asana pagination-limit 400s but fails on other 400s."""
    manifest = _load_manifest()

    response_filters = manifest["definitions"]["requester"]["error_handler"]["response_filters"]

    pagination_filter = None
    generic_400_filter = None
    for f in response_filters:
        if f.get("error_message_contains") == "upper limit on the number of results":
            pagination_filter = f
        if f.get("action") == "FAIL" and 400 in (f.get("http_codes") or []):
            generic_400_filter = f

    assert pagination_filter is not None, "Pagination-limit IGNORE filter must exist in manifest"
    assert generic_400_filter is not None, "Generic HTTP 400 FAIL filter must exist in manifest"

    error_msg = json_body.get("errors", [{}])[0].get("message", "")

    if "upper limit on the number of results" in error_msg:
        assert pagination_filter["action"] == expected_action.name
    else:
        assert generic_400_filter["action"] == expected_action.name


def test_pagination_limit_filter_precedes_generic_400():
    """The IGNORE filter must come before the generic HTTP 400 FAIL filter."""
    manifest = _load_manifest()
    response_filters = manifest["definitions"]["requester"]["error_handler"]["response_filters"]

    pagination_idx = None
    generic_400_idx = None
    for idx, f in enumerate(response_filters):
        if f.get("error_message_contains") == "upper limit on the number of results":
            pagination_idx = idx
        if f.get("action") == "FAIL" and 400 in (f.get("http_codes") or []):
            generic_400_idx = idx

    assert pagination_idx is not None, "Pagination-limit IGNORE filter must exist"
    assert generic_400_idx is not None, "Generic HTTP 400 FAIL filter must exist"
    assert pagination_idx < generic_400_idx, (
        f"Pagination-limit filter (index {pagination_idx}) must precede " f"generic 400 filter (index {generic_400_idx})"
    )


def test_pagination_limit_filter_has_no_http_codes():
    """The IGNORE filter must NOT specify http_codes to avoid matching all 400s."""
    manifest = _load_manifest()
    response_filters = manifest["definitions"]["requester"]["error_handler"]["response_filters"]

    for f in response_filters:
        if f.get("error_message_contains") == "upper limit on the number of results":
            assert "http_codes" not in f, (
                "Pagination-limit IGNORE filter must not specify http_codes " "(relies solely on error_message_contains matching)"
            )
            return

    pytest.fail("Pagination-limit IGNORE filter not found in manifest")
