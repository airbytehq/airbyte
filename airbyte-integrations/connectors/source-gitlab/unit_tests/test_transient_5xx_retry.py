#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _response_filters() -> list[dict]:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    return manifest["definitions"]["requester"]["error_handler"]["response_filters"]


@pytest.mark.parametrize(
    "status_code,expected_action",
    [
        pytest.param(500, "RETRY", id="server_error_is_retried"),
        pytest.param(502, "RETRY", id="bad_gateway_is_retried"),
        pytest.param(503, "RETRY", id="service_unavailable_is_retried"),
        pytest.param(403, "IGNORE", id="forbidden_is_ignored"),
        pytest.param(401, "FAIL", id="unauthorized_still_fails"),
    ],
)
def test_error_handler_action_for_status(status_code, expected_action):
    filters = _response_filters()
    matched = [f for f in filters if status_code in f.get("http_codes", [])]
    assert matched, f"no response filter matches {status_code}"
    assert matched[0]["action"] == expected_action
