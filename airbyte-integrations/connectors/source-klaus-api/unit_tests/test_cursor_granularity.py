# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Regression tests for the cursor_granularity / datetime_format mismatch bug.

When `cursor_granularity` (PT0.001S) is finer than `datetime_format` precision
(second-level `%Y-%m-%dT%H:%M:%SZ`), the CDK's concurrent cursor
`merge_intervals` cannot bridge the gap between serialized slice boundaries.
The per-partition cursor stays pinned near the start date and the stream
re-reads its entire history every sync.

The fix sets `cursor_granularity: PT1S` so slice boundaries survive
round-trip formatting and intervals merge correctly.

See: https://github.com/airbytehq/oncall/issues/12928
Prior art: https://github.com/airbytehq/airbyte/pull/80282 (source-twilio)
"""

from pathlib import Path

import pytest
import requests_mock as rm
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path / "manifest.yaml"
    return Path(__file__).parent.parent / "manifest.yaml"


_CONFIG = {
    "api_key": "test-api-key",
    "account": 123,
    "workspace": 456,
    "start_date": "2024-01-01T00:00:00Z",
}

_BASE_URL = "https://kibbles.klausapp.com/api/v2"
_REVIEWS_PATH = f"/account/{_CONFIG['account']}/workspace/{_CONFIG['workspace']}/reviews"


def test_manifest_cursor_granularity_matches_datetime_format():
    """The manifest must declare `cursor_granularity: PT1S` (not sub-second)
    for streams using second-precision `datetime_format`."""
    manifest = yaml.safe_load(_manifest_path().read_text())
    inc = manifest["definitions"]["streams"]["reviews"]["incremental_sync"]

    assert inc["cursor_granularity"] == "PT1S", (
        f"cursor_granularity must be PT1S to match the second-precision datetime_format, got {inc['cursor_granularity']!r}"
    )
    assert "%" in inc["datetime_format"] and "%f" not in inc["datetime_format"], (
        "datetime_format should be second-precision (no %f microsecond directive)"
    )


@pytest.mark.parametrize(
    "saved_cursor,record_cursor",
    [
        pytest.param(
            "2024-01-15T00:00:00Z",
            "2024-01-20T00:00:00Z",
            id="mid-month-advance",
        ),
        pytest.param(
            "2024-01-01T00:00:00Z",
            "2024-01-28T12:30:00Z",
            id="full-month-advance",
        ),
    ],
)
def test_reviews_cursor_advances_across_windows(saved_cursor, record_cursor):
    """With PT1S granularity, the cursor must advance past the saved state
    after an incremental sync that returns newer records."""
    catalog = CatalogBuilder().with_stream("reviews", SyncMode.incremental).build()
    state = StateBuilder().with_stream_state("reviews", {"lastUpdatedISO": saved_cursor}).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(_manifest_path()),
        catalog=catalog,
        config=_CONFIG,
        state=state,
    )

    def _reviews_callback(request, context):
        context.status_code = 200
        return {"conversations": [{"lastUpdatedISO": record_cursor, "id": "conv-1"}]}

    with rm.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{_REVIEWS_PATH}", json=_reviews_callback)
        output = read(source, _CONFIG, catalog, state)

    assert output.state_messages, "expected at least one state message"

    final_state = output.state_messages[-1].state
    final_cursor = final_state.stream.stream_state.__dict__.get("lastUpdatedISO", "")

    assert final_cursor > saved_cursor, (
        f"per-stream cursor did not advance past saved value (stuck at {final_cursor!r}, saved was {saved_cursor!r})"
    )
    assert final_cursor == record_cursor, f"expected cursor to advance to {record_cursor!r}, got {final_cursor!r}"
