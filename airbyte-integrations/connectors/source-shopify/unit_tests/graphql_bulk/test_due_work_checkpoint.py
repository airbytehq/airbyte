"""Generated due-work checks for Shopify bulk checkpoint continuation.

Run on Python 3.11 with due-work-harness installed. The connector also supports
Python 3.10, which the harness does not yet support.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests
from source_shopify.streams.streams import Products


pytest.importorskip("due_work_harness")

from due_work_harness import Host, configure  # noqa: E402
from due_work_harness.contract import (  # noqa: E402
    Adoption,
    Decline,
    DueWorkContract,
    NotApplicable,
    Profile,
    SafetyContract,
    SafetyProfile,
    due_work_contract_suite,
)
from due_work_harness.crash_histories import Findings  # noqa: E402
from due_work_harness.process_histories import ProcessHistory, fault_environment, fault_fires  # noqa: E402


CONFIG = {
    "shop": "test-shop",
    "start_date": "2023-01-01",
    "credentials": {"auth_method": "api_password", "api_password": "api_password"},
    "authenticator": None,
}


def _response(*, url: str | None, count: int, status: str) -> requests.Response:
    result = requests.Response()
    result.status_code = 200
    result._content = json.dumps(
        {"data": {"node": {"status": status, "objectCount": str(count), "url": url, "partialDataUrl": None}}}
    ).encode()
    return result


def _url(name: str) -> str:
    return f"https://storage.googleapis.com/bulk?response-content-disposition=attachment%3B+filename%3D%22{name}%22"


def _download_response(product_id: int, updated_at: str) -> requests.Response:
    result = requests.Response()
    result.status_code = 200
    result._content = (
        json.dumps({"__typename": "Product", "id": f"gid://shopify/Product/{product_id}", "updatedAt": updated_at}) + "\n"
    ).encode()
    result.iter_content = Mock(return_value=iter((result._content,)))
    return result


def _run_sync(directory: Path) -> None:
    # ARRANGE: a checkpointable product sync reads two adjacent one-day slices.
    previous = Path.cwd()
    os.chdir(directory)
    try:
        stream = Products(CONFIG)
        manager = stream.job_manager
        manager._job_size = 1
        slices = iter(stream.stream_slices())
        first = next(slices)
        emitted = []
        state = {stream.cursor_field: CONFIG["start_date"]}

        def download(*, url: str, **kwargs):
            # EXTERNAL SEAM: Shopify's bulk-result storage returns one product per URL.
            if "first.jsonl" in url:
                return None, _download_response(1, "2023-01-01T12:00:00Z")
            return None, _download_response(2, "2023-01-02T06:00:00Z")

        manager.http_client.send_request = Mock(side_effect=download)
        manager._job_self_canceled = True
        manager._job_last_rec_count = 4
        missing_url = fault_fires("canceled without partial result URL")

        # REAL PRODUCTION: a self-canceled job attempts to checkpoint, then the
        # real stream advances its slice iterator using the manager's state.
        manager._on_canceled_job(_response(url=None if missing_url else _url("first.jsonl"), count=4, status="CANCELED"))
        if manager._job_result_filename:
            records = manager.record_producer.read_file(manager._job_result_filename)
            for record in stream.filter_records_newer_than_state(state, records):
                emitted.append(record["id"])
                state = stream.get_updated_state(state, record)

        second = next(slices)
        manager._on_completed_job(_response(url=_url("second.jsonl"), count=1, status="COMPLETED"))
        records = manager.record_producer.read_file(manager._job_result_filename)
        for record in stream.filter_records_newer_than_state(state, records):
            emitted.append(record["id"])
            state = stream.get_updated_state(state, record)

        # OBSERVE: persisted state after the later record controls the next sync.
        (directory / "result.json").write_text(json.dumps({"emitted": emitted, "state": state, "first": first, "second": second}))
        if missing_url:
            sys.exit(1)
    finally:
        os.chdir(previous)


def _run_history(point: str | None) -> tuple[Path, int]:
    # ARRANGE: each history runs the same connector path in a fresh child.
    directory = Path(tempfile.mkdtemp(prefix="shopify-checkpoint-"))
    child = subprocess.run(
        [sys.executable, __file__, "child", str(directory)],
        env={**os.environ, **fault_environment(point)},
        capture_output=True,
        text=True,
    )
    if child.returncode not in (0, 1) or not (directory / "result.json").exists():
        raise AssertionError(child.stderr)
    # REAL PRODUCTION: _run_sync calls the connector's job manager and stream.
    # EXTERNAL SEAM: only the two Shopify responses are supplied by this file.
    # OBSERVE: the result file records emitted product IDs and checkpoint state.
    return directory, child.returncode


def _observe(directory: Path) -> tuple[tuple[int, ...], str | None]:
    # ARRANGE: the child wrote its result after processing both slices.
    if not (directory / "result.json").exists():
        return (), None
    result = json.loads((directory / "result.json").read_text())
    # REAL PRODUCTION: emitted IDs and state came from the actual stream methods.
    # EXTERNAL SEAM: the Shopify response is deterministic across histories.
    # OBSERVE: a later state excludes the missing first-slice record on retry.
    return tuple(result["emitted"]), result.get("retry_start")


def _recover(directory: Path) -> None:
    # ARRANGE: Airbyte retries a sync from the last emitted state.
    result = json.loads((directory / "result.json").read_text())
    stream = Products(CONFIG)
    # REAL PRODUCTION: the connector's own slice generator calculates retry range.
    retry_slice = next(iter(stream.stream_slices(stream_state=result["state"])))
    # EXTERNAL SEAM: no Shopify call is required to inspect the requested range.
    # OBSERVE: record where a platform retry would begin.
    result["retry_start"] = retry_slice["start"]
    (directory / "result.json").write_text(json.dumps(result))


configure(Host(production_packages=frozenset({"source_shopify"})))

SHOPIFY_BULK_CHECKPOINT = DueWorkContract(
    name="Airbyte Shopify bulk checkpoint continuation",
    adoption=Adoption.LEGACY,
    profiles={
        Profile.A: Decline("Airbyte platform schedules sync retries; the connector has no durable retry sweep"),
        Profile.B: NotApplicable("one connector process owns each local bulk result"),
        Profile.C: Decline("Shopify bulk operation creation has no persisted attempt record in the connector"),
        Profile.D: NotApplicable("the connector has no durable due-work retention pass"),
        Profile.E: NotApplicable("bulk result files are consumed by one stream, without competing snapshot writes"),
        Profile.F: Decline("Airbyte platform state, rather than this connector, determines which sync is due"),
    },
    safety=SafetyContract(
        name="Airbyte Shopify bulk checkpoint continuation",
        adoption=Adoption.LEGACY,
        profiles={
            SafetyProfile.REPLAY_SAFE_EXECUTION: Decline("Shopify bulk operation creation can be replayed after an uncertain outcome"),
            SafetyProfile.BOUNDED_RETRY: Decline("connector retry budget is separate from this checkpoint boundary"),
        },
    ),
    process_handoffs=(
        ProcessHistory(
            name="self-canceled bulk job without partial result URL",
            initial=((), None),
            run=_run_history,
            observe=_observe,
            recover=_recover,
            death_points=(),
            failure_points=("canceled without partial result URL",),
            findings=Findings(
                delivered=((1, 2), "2023-01-02T06:00:00+00:00"),
                outcomes={"canceled without partial result URL": ((2,), "2023-01-02T06:00:00+00:00")},
            ),
        ),
    ),
    handoff_gaps={
        "self-canceled bulk job without partial result URL": "#85372: a self-canceled job with no partialDataUrl skips its undownloaded slice",
    },
)


# The decorator generates every test in this class from the production-bound
# contract above. The missing-URL history is a strict legacy XFAIL: a fix makes
# the case pass and forces the gap declaration to be removed.
@due_work_contract_suite(SHOPIFY_BULK_CHECKPOINT)
class TestShopifyBulkCheckpointDueWork:
    pass


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "child":
    _run_sync(Path(sys.argv[2]))
