# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Regression test for the stuck-cursor bug (oncall #12927).

The `logs` stream uses a second-precision `datetime_format` (`%Y-%m-%dT%H:%M:%SZ`).
If `cursor_granularity` is finer than that (e.g. `PT0.000001S`), each slice end
(`next_start - granularity`) is truncated when formatted, opening a gap between
consecutive slice intervals that `merge_intervals` cannot bridge. The per-partition
cursor then never advances and the stream re-reads its whole history every sync.

With a matching granularity (`PT1S`) the intervals merge and the cursor advances.
"""

from urllib.parse import parse_qs, urlparse

from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.datadoghq.com/api"


def _read_logs(cfg, state=None):
    catalog = CatalogBuilder().with_stream("logs", SyncMode.incremental).build()
    return read(get_source(cfg, state), cfg, catalog, state)


@freeze_time("2022-06-15T12:00:00Z")
def test_logs_cursor_advances_across_windows(requests_mock):
    """Per-partition cursor must advance past the saved value after reading new data."""

    def _logs_response(request, context):
        qs = parse_qs(urlparse(request.url).query, keep_blank_values=True)
        from_ts = qs.get("filter[from]", ["1970-01-01T00:00:00Z"])[0]
        context.status_code = 200
        return {
            "data": [
                {
                    "id": f"log-{from_ts}",
                    "type": "log",
                    "attributes": {"timestamp": from_ts},
                }
            ]
        }

    requests_mock.get(f"{BASE}/v2/logs/events", json=_logs_response)

    saved_cursor = "2022-03-01T00:00:00Z"
    state = (
        StateBuilder()
        .with_stream_state(
            "logs",
            {
                "states": [
                    {
                        "partition": {},
                        "cursor": {"sync_date": saved_cursor},
                    }
                ],
                "state": {"sync_date": saved_cursor},
                "use_global_cursor": False,
            },
        )
        .build()
    )

    output = _read_logs(TEST_CONFIG, state)

    records = output.records
    assert len(records) > 0, "Expected at least one record from the logs stream"

    final = output.most_recent_state.stream_state.__dict__
    cursor_value = final.get("sync_date") or final.get("state", {}).get("sync_date", saved_cursor)
    assert cursor_value > saved_cursor, (
        f"Cursor did not advance past saved value {saved_cursor} (got {cursor_value}). "
        "This indicates cursor_granularity is finer than datetime_format precision."
    )
