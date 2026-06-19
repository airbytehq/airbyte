# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.datadoghq.com/api"


def read_from_stream(cfg, stream: str, sync_mode, state=None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(get_source(cfg, state), cfg, catalog, state, False)


@freeze_time("2024-06-01 00:00:00+00:00")
def test_logs_cursor_advances_across_windows(requests_mock):
    """Regression for the stuck-cursor bug (oncall airbytehq/oncall#12927).

    The `logs` stream uses second-precision `datetime_format` (`%Y-%m-%dT%H:%M:%SZ`).
    If `cursor_granularity` is finer than that (e.g. `PT0.000001S`), each slice end
    is truncated to the second when formatted, opening a ~1s gap between consecutive
    slice intervals that `merge_intervals` cannot bridge. The per-partition cursor
    then never advances past the first window and the stream re-reads its whole
    history every sync. With a matching granularity (`PT1S`) the intervals merge
    and the cursor advances to the newest record.

    This two-pass test verifies the fix: sync 1 reads data and produces state,
    sync 2 uses that state and should read fewer records (proving the cursor
    advanced rather than staying pinned near the start).
    """
    call_log = []

    def _logs_response(request, context):
        qs = parse_qs(urlparse(request.url).query)
        filter_from = qs.get("filter[from]", [""])[0]
        call_log.append(filter_from)
        context.status_code = 200
        return {
            "data": [
                {
                    "id": f"log-{filter_from}",
                    "type": "log",
                    "attributes": {
                        "timestamp": filter_from,
                        "host": "test-host",
                        "message": "test",
                        "service": "test-svc",
                        "status": "info",
                        "tags": [],
                    },
                }
            ],
            "links": {},
        }

    requests_mock.get(f"{BASE}/v2/logs/events", json=_logs_response)

    saved_cursor = "2024-02-01T00:00:00Z"
    state = StateBuilder().with_stream_state("logs", {"sync_date": saved_cursor}).build()

    # --- Sync 1: read from the saved cursor ---
    output_1 = read_from_stream(TEST_CONFIG, "logs", SyncMode.incremental, state)
    sync_1_calls = len(call_log)
    assert sync_1_calls > 0, "sync 1 should have made at least one API call"

    # Capture the state emitted by sync 1
    final_state_1 = output_1.most_recent_state.stream_state.__dict__
    cursor_after_sync_1 = final_state_1.get("sync_date", saved_cursor)
    assert cursor_after_sync_1 > saved_cursor, f"sync 1 cursor did not advance (stuck at {cursor_after_sync_1!r})"

    # --- Sync 2: use the state from sync 1 ---
    call_log.clear()
    state_2 = StateBuilder().with_stream_state("logs", final_state_1).build()
    output_2 = read_from_stream(TEST_CONFIG, "logs", SyncMode.incremental, state_2)
    sync_2_calls = len(call_log)

    # With a working cursor, sync 2 should make fewer calls than sync 1
    # because the cursor advanced past most of the date range.
    assert sync_2_calls < sync_1_calls, (
        f"sync 2 made {sync_2_calls} calls (same or more than sync 1's {sync_1_calls}); "
        f"cursor appears stuck — the stream is re-reading its full history"
    )
