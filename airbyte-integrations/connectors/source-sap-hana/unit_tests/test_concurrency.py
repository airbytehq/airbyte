import itertools
import threading
import time

import pytest
from airbyte_cdk.models import AirbyteStreamStatus, SyncMode, Type
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from source_sap_hana import SourceSapHana
from source_sap_hana.concurrency import interleave

from .test_source import ACDOCA_COLUMNS, ACDOCA_ROWS, configured_catalog


def test_interleave_keeps_each_producer_ordered_and_respects_max_workers():
    active = 0
    peak = 0
    lock = threading.Lock()

    def producer(name):
        def run():
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            try:
                for i in range(50):
                    time.sleep(0.0005)
                    yield (name, i)
            finally:
                with lock:
                    active -= 1

        return run

    items = list(interleave([producer(n) for n in "abcde"], max_workers=2, buffer_size=5))
    assert len(items) == 250
    for name in "abcde":
        assert [i for n, i in items if n == name] == list(range(50))
    assert peak == 2


def test_interleave_stops_workers_when_consumer_closes_early():
    produced = []

    def endless():
        for i in itertools.count():
            produced.append(i)
            yield i

    gen = interleave([endless, endless], max_workers=2, buffer_size=3)
    assert next(gen) == 0
    started = time.monotonic()
    gen.close()  # must not hang
    assert time.monotonic() - started < 5
    count = len(produced)
    time.sleep(0.3)
    assert len(produced) == count  # workers really stopped


def test_interleave_propagates_producer_errors():
    def boom():
        yield 1
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        list(interleave([boom], max_workers=2))


def _many_tables(hana, n=6, rows=25):
    for t in range(n):
        hana.add_table(
            f"T{t}",
            [("ID", "INTEGER"), ("VAL", "NVARCHAR")],
            [(i, f"t{t}-{i}") for i in range(rows)],
            pk=["ID"] if t % 2 == 0 else [],
        )


def test_concurrent_read_matches_sequential(hana, config, logger):
    _many_tables(hana)
    config.update(full_refresh_page_size=7)
    source = SourceSapHana()
    names = [f"T{t}" for t in range(6)]

    def run(workers):
        config["max_concurrent_streams"] = workers
        catalog = configured_catalog(source, config, logger, names)
        messages = list(source.read(logger, config, catalog, []))
        records = sorted((m.record.stream, m.record.data["ID"]) for m in messages if m.type == Type.RECORD)
        final_states = {}
        for m in messages:
            if m.type == Type.STATE:
                final_states[m.state.stream.stream_descriptor.name] = dict(m.state.stream.stream_state.__dict__)
        statuses = [m.trace.stream_status for m in messages if m.type == Type.TRACE and m.trace.stream_status]
        completed = [st.stream_descriptor.name for st in statuses if st.status == AirbyteStreamStatus.COMPLETE]
        return records, final_states, sorted(completed)

    assert run(4) == run(1)
    records, states, completed = run(4)
    assert len(records) == 6 * 25
    assert completed == names
    assert states["T0"] == {"__ab_full_refresh_sync_complete": True}
    assert states["T1"] == {"__ab_no_cursor_state_message": True}


def test_concurrent_read_keeps_per_stream_message_order(hana, config, logger):
    hana.add_table("ACDOCA", ACDOCA_COLUMNS, ACDOCA_ROWS, pk=["RCLNT", "BELNR", "DOCLN"])
    _many_tables(hana, n=3)
    config.update(max_concurrent_streams=4, checkpoint_interval=1)
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"])
    catalog.streams += configured_catalog(source, config, logger, ["T0", "T1", "T2"]).streams

    def is_acdoca(m):
        if m.type == Type.RECORD:
            return m.record.stream == "ACDOCA"
        return m.type == Type.STATE and m.state.stream.stream_descriptor.name == "ACDOCA"

    messages = [m for m in source.read(logger, config, catalog, []) if is_acdoca(m)]
    # For each state, every record emitted before it must have a cursor <= the checkpointed value.
    seen = []
    for m in messages:
        if m.type == Type.RECORD:
            seen.append(m.record.data["TIMESTAMP"])
        else:
            assert all(v <= m.state.stream.stream_state.cursor for v in seen)
    assert len(seen) == len(ACDOCA_ROWS)


def test_concurrent_read_isolates_failing_stream(hana, config, logger):
    _many_tables(hana, n=4)
    config.update(max_concurrent_streams=3, resumable_full_refresh=False, max_retries=0)
    hana.fail_after_rows = [5]  # the first data query to run fails mid-stream
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["T0", "T1", "T2", "T3"])
    messages = []
    with pytest.raises(AirbyteTracedException, match="1 stream"):
        for m in source.read(logger, config, catalog, []):
            messages.append(m)
    statuses = [m.trace.stream_status.status for m in messages if m.type == Type.TRACE and m.trace.stream_status]
    assert statuses.count(AirbyteStreamStatus.COMPLETE) == 3
    assert statuses.count(AirbyteStreamStatus.INCOMPLETE) == 1
