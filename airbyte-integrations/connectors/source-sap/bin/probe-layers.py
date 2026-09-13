#!/usr/bin/env python3
"""Where does the time go in an RFC extract?

The third measurement tool, between the other two:

  * `benchmark.py` runs the connector as the platform does and times it,
  * this one runs the driver's own SQL against DuckDB directly, so it can vary
    the thread budget, the partition count and erpl's RFC thread pool without
    the CDK in the way,
  * `trace-round-trips.py` counts what SAP was actually asked to do.

Two rules keep its answers usable, learned the hard way -- four explanations of
the partitioning result were published from probes that were not measuring the
connector's workload:

  * the SQL comes from `RfcDriver.read_plans`, so it is what the connector runs,
    not a hand-written approximation;
  * every row is pulled through `fetchmany` exactly as `records_from` does, so
    DuckDB cannot skip reading the columns.

    poetry run ./bin/probe-layers.py                 # the default matrix
    poetry run ./bin/probe-layers.py --narrow        # two columns instead of all 55
    poetry run ./bin/probe-layers.py --connections   # RFC connections each path uses

Needs the same environment as the e2e suite; see bin/test-e2e.sh.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import duckdb  # noqa: E402

from source_sap.duck import columns_of  # noqa: E402
from source_sap.protocols.base import FETCH_BATCH, SapObject  # noqa: E402
from source_sap.protocols.rfc import RfcDriver  # noqa: E402
from source_sap.types import coerce_row  # noqa: E402

TABLE = "DD02L"
NARROW = ["TABNAME", "TABCLASS"]
TRACE_DIR = pathlib.Path("/tmp/erpl-layer-probe")


def connection_config() -> dict[str, str]:
    return {
        "ashost": os.environ.get("ERPL_SAP_ASHOST", "localhost"),
        "sysnr": os.environ.get("ERPL_SAP_SYSNR", "00"),
        "client": os.environ.get("ERPL_SAP_CLIENT", "001"),
        "user": os.environ.get("ERPL_SAP_USER", "DEVELOPER"),
        "password": os.environ.get("ERPL_SAP_PASSWORD", ""),
        "lang": os.environ.get("ERPL_SAP_LANG", "EN"),
    }


def sql_for(partitions: int, rfc_threads: int | None, columns: list[str] | None) -> str:
    """The connector's own SQL for this configuration."""
    obj: dict = {"name": TABLE, "partitions": partitions}
    if rfc_threads is not None:
        obj["threads"] = rfc_threads
    if columns:
        obj["columns"] = columns
    driver = RfcDriver({**connection_config(), "protocol": {"mode": "rfc", "objects": [obj]}})
    target = SapObject(name=TABLE, json_schema={}, meta={"table": TABLE})
    return driver.read_plans(None, target, incremental=False, state={})[0].sql


def connect(threads: int, trace: bool = False) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(
        config={
            "allow_unsigned_extensions": "true",
            "extension_directory": os.environ["ERPL_EXTENSION_DIR"],
            "threads": str(threads),
        }
    )
    con.load_extension("erpl_rfc")
    con.execute("SET erpl_telemetry_enabled = false")
    if trace:
        shutil.rmtree(TRACE_DIR, ignore_errors=True)
        TRACE_DIR.mkdir(parents=True, exist_ok=True)
        con.execute(f"PRAGMA sap_rfc_set_trace_dir('{TRACE_DIR}')")
        con.execute("PRAGMA sap_rfc_set_trace_level(3)")
    config = connection_config()
    con.execute(
        "CREATE OR REPLACE SECRET p (TYPE sap_rfc, ASHOST $h, SYSNR $n, CLIENT $c, USER $u, PASSWD $p, LANG $l)",
        {
            "h": config["ashost"],
            "n": config["sysnr"],
            "c": config["client"],
            "u": config["user"],
            "p": config["password"],
            "l": config["lang"],
        },
    )
    return con


def measure(threads, partitions, *, rfc_threads=None, columns=None, convert=False, trace=False):
    con = connect(threads, trace=trace)
    try:
        start = time.perf_counter()
        result = con.execute(sql_for(partitions, rfc_threads, columns))
        names = columns_of(result.description)
        rows = 0
        while True:
            batch = result.fetchmany(FETCH_BATCH)
            if not batch:
                break
            if convert:
                for row in batch:
                    coerce_row(names, row)
            rows += len(batch)
        return rows, time.perf_counter() - start
    finally:
        con.close()


def report(label, rows, elapsed):
    print(f"{label:<44}{rows:>10,}{elapsed:>9.1f}s{rows / elapsed:>11,.0f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--narrow", action="store_true", help="two columns instead of all 55")
    parser.add_argument("--connections", action="store_true", help="count the RFC connections each path opens")
    args = parser.parse_args()
    columns = NARROW if args.narrow else None

    if args.connections:
        # One trace file per RFC connection, so the file count is the concurrency.
        for partitions in (0, 8):
            measure(8, partitions, columns=columns, trace=True)
            files = {f.name: f.read_text(errors="replace").count(">> ROWSKIPS") for f in TRACE_DIR.rglob("*.trc")}
            busy = {name: n for name, n in files.items() if n}
            print(
                f"partitions={partitions}: {sum(busy.values())} RFC calls across "
                f"{len(busy)} connections ({sorted(busy.values(), reverse=True)})"
            )
        shutil.rmtree(TRACE_DIR, ignore_errors=True)
        return

    print(f"{'case':<44}{'rows':>10}{'seconds':>10}{'rows/s':>11}")
    for threads in (1, 2, 4, 8, 16, 32):
        report(f"serial, {threads} duckdb threads", *measure(threads, 0, columns=columns))
    for rfc_threads in (1, 4, 16):
        report(
            f"serial, 16 threads, THREADS := {rfc_threads}",
            *measure(16, 0, rfc_threads=rfc_threads, columns=columns),
        )
    for threads in (1, 8, 32):
        report(f"8 partitions, {threads} duckdb threads", *measure(threads, 8, columns=columns))
    report("8 partitions, THREADS := 55", *measure(16, 8, rfc_threads=55, columns=columns))
    report("serial, 16 threads, with coerce_row", *measure(16, 0, columns=columns, convert=True))


if __name__ == "__main__":
    main()
