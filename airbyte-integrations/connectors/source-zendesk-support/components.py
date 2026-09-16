# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import atexit
import sys
import time
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


def _force_fail_pre_exit_sleep() -> None:
    """DO NOT MERGE — workaround for an orchestrator race that loses connector trace messages.

    The container orchestrator's MessageProcessor coroutine drains the source-message queue
    (and is what calls `messageTracker.acceptFromSource`, populating the trace-derived
    FailureReasons) on a coroutine separate from the SourceReader. When the source process
    exits non-zero, SourceReader throws SourceException; structured concurrency in
    `runJobs { coroutineScope { tasks.awaitAll() } }` then cancels MessageProcessor —
    regardless of whether the queue has been drained. Anything still queued (very often
    including the ERROR TRACE that was emitted right before exit) is silently dropped.

    The 10-second sleep inside `LocalContainerAirbyteSource.exitValue` (waiting for the
    exit-code file when the pipe closes first) is what intermittently saves us in
    production: it delays SourceException long enough for MessageProcessor to drain.

    This atexit hook recreates that delay deterministically: flush stdout/stderr so the
    trace bytes are on the wire, then sleep so the orchestrator's reader has time to parse
    them and MessageProcessor has time to call `acceptFromSource(...)` before the pipe
    closes and SourceException tears down sibling coroutines.
    """
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception:  # noqa: BLE001 — best-effort flush, never block exit
        pass
    time.sleep(10)


atexit.register(_force_fail_pre_exit_sleep)


class ForceFailError(RuntimeError):
    """Plain Python exception raised by `ForceFailExtractor` for pre-release testing.

    DO NOT MERGE — inherits from `RuntimeError` rather than
    `airbyte_cdk.utils.traced_exception.AirbyteTracedException` so the CDK has
    to wrap a vanilla Python exception (no curated `failure_type`, no
    user-facing `message`). This mirrors what the platform sees when a
    connector hits an unhandled bug in the wild.
    """


@dataclass
class ForceFailExtractor(RecordExtractor):
    """Record extractor that force-fails every record extraction.

    DO NOT MERGE — this extractor exists solely to produce a pre-release image
    that fails every sync on the read path. The HTTP request, authentication,
    and response are all left intact; the failure is raised when the platform
    asks the connector to extract records from the response. Every stream's
    `read` therefore fails with a `ForceFailError` (a plain `RuntimeError`
    subclass).
    """

    parameters: InitVar[Mapping[str, Any]]

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        raise ForceFailError("source-zendesk-support pre-release force-fail injection. DO NOT MERGE.")


class ZendeskSupportExtractorEvents(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = response.json().get("ticket_events") or []
        except requests.exceptions.JSONDecodeError:
            records = []

        events = []
        for record in records:
            for event in record.get("child_events", []):
                if event.get("event_type") == "Comment":
                    for prop in ["via_reference_id", "ticket_id", "timestamp"]:
                        event[prop] = record.get(prop)

                    # https://github.com/airbytehq/oncall/issues/1001
                    if not isinstance(event.get("via"), dict):
                        event["via"] = None
                    events.append(event)
        return events


class ZendeskSupportAttributeDefinitionsExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = []
            for definition in response.json()["definitions"]["conditions_all"]:
                definition["condition"] = "all"
                records.append(definition)
            for definition in response.json()["definitions"]["conditions_any"]:
                definition["condition"] = "any"
                records.append(definition)
        except requests.exceptions.JSONDecodeError:
            records = []
        return records


class TicketsStateMigration(StateMigration):
    """Migrates tickets stream state from the `updated_at` cursor back to `generated_timestamp`.

    Background: v5.2.0 switched the `tickets` stream from the Incremental Ticket Export API
    (keyed on `generated_timestamp`) to the Export Search Results API (filtered/checkpointed on
    `updated_at`). Because Zendesk only bumps `updated_at` when an update generates a ticket
    event, automation/macro/system-driven updates were silently dropped. We revert the stream to
    `generated_timestamp`, so existing connections carrying `updated_at`-based state must be
    migrated back.

    Backfill: to recover every ticket missed while the regression was live, the migrated cursor
    is clamped back to an absolute floor of 2026-03-01T00:00:00Z (epoch 1772323200) — just before
    v5.2.0 merged (2026-03-12) / rolled out to Cloud (~2026-03-24). This guarantees a complete
    one-time backfill regardless of when a connection upgrades (a relative "N-day" window computed
    at migration time would drift forward and miss the earliest affected tickets). `min(...)`
    ensures we only ever pull the cursor back, never forward, so connections whose cursor has not
    yet reached the floor are left untouched.

    Only connections that ran the buggy `updated_at`-cursor versions carry `updated_at` state, so
    keying `should_migrate` on that field means the floor is applied exactly once (on the first
    sync after upgrade); subsequent syncs write `generated_timestamp` state and are left alone.
    Connections still on a pre-5.2.0 `generated_timestamp` cursor were never broken and are not
    migrated.
    """

    # 2026-03-01T00:00:00Z
    BACKFILL_FLOOR = 1772323200

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and "updated_at" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            cursor_value = int(stream_state["updated_at"])
        except (KeyError, TypeError, ValueError):
            cursor_value = self.BACKFILL_FLOOR
        return {"generated_timestamp": min(cursor_value, self.BACKFILL_FLOOR)}
