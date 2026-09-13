#!/usr/bin/env python3
"""Count the RFC round trips behind a partitioned scan.

The companion to `benchmark.py`: that one measures the connector end to end,
this one asks what the SAP side actually did. It exists because four attempts to
explain the partitioning result from timings were each wrong -- the queries let
DuckDB skip reading the columns, so they were not measuring the connector's
workload at all.

Two rules make its answers usable:

  * the query casts the row to VARCHAR, which defeats projection pushdown, so
    every column is really fetched;
  * the conclusion comes from counting RFC calls in erpl's own trace, not from
    the clock. `>> ROWSKIPS` appears once per RFC_READ_TABLE invocation that
    sets the parameter, so it counts round trips. (Matching bare
    "RFC_READ_TABLE" also catches the SDK's metadata chatter and overcounts.)

This produced the round-trip table in docs/performance.md.

    ./bin/trace-round-trips.py

Needs the same environment as the e2e suite; see bin/test-e2e.sh.
"""

import os
import shutil
import time
from pathlib import Path

import duckdb

TRACE_DIR = Path("/tmp/erpl-fetchsize-probe")
DEFAULT_FETCH = 1_310_720
ROWS = 164_673


def connect():
    shutil.rmtree(TRACE_DIR, ignore_errors=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(
        config={
            "allow_unsigned_extensions": "true",
            "extension_directory": os.environ["ERPL_EXTENSION_DIR"],
            "memory_limit": "4GB",
            "threads": "8",
        }
    )
    con.load_extension("erpl_rfc")
    con.execute("SET erpl_telemetry_enabled = false")
    con.execute(f"PRAGMA sap_rfc_set_trace_dir('{TRACE_DIR}')")
    con.execute("PRAGMA sap_rfc_set_trace_level(3)")
    con.execute(
        "CREATE SECRET p (TYPE sap_rfc, ASHOST $h, SYSNR $n, CLIENT $c, USER $u, PASSWD $p, LANG $l)",
        {
            "h": os.environ.get("ERPL_SAP_ASHOST", "localhost"),
            "n": "00",
            "c": "001",
            "u": os.environ.get("ERPL_SAP_USER", "DEVELOPER"),
            "p": os.environ.get("ERPL_SAP_PASSWORD", ""),
            "l": "EN",
        },
    )
    return con


def round_trips() -> int:
    return sum(p.read_text(errors="replace").count(">> ROWSKIPS") for p in TRACE_DIR.rglob("*.trc"))


print(f"{'configuration':<38}{'time':>9}{'rows/s':>11}{'RFC calls':>11}{'rows/call':>11}")
cases = [
    ("serial, default fetch_size", 0, None),
    ("8 partitions, default fetch_size", 8, None),
    ("8 partitions, 8x fetch_size", 8, DEFAULT_FETCH * 8),
    ("8 partitions, 32x fetch_size", 8, DEFAULT_FETCH * 32),
]
try:
    for label, partitions, fetch_size in cases:
        args = ["'DD02L'", f"PARTITIONS := {partitions}"]
        if fetch_size:
            args.append(f"FETCH_SIZE := {fetch_size}")
        sql = f"SELECT sum(length(CAST(t AS VARCHAR))) FROM (SELECT * FROM sap_read_table({', '.join(args)})) t"
        con = connect()
        start = time.perf_counter()
        try:
            con.execute(sql).fetchone()
            elapsed = time.perf_counter() - start
        except Exception as exc:
            print(f"{label:<38}  FAILED: {str(exc)[:50]}")
            continue
        finally:
            # The trace is only complete once the connection is closed, and an
            # interrupt here would otherwise leave an open SAP session behind.
            con.close()
        calls = round_trips()
        print(f"{label:<38}{elapsed:>8.1f}s{ROWS / elapsed:>11,.0f}{calls:>11,}{ROWS / calls if calls else 0:>11,.0f}")
finally:
    # Traces are large and the directory is scratch, so it goes whatever happened.
    shutil.rmtree(TRACE_DIR, ignore_errors=True)
