#!/usr/bin/env python3
"""Measure end-to-end replication throughput for source-sap.

Runs the connector exactly as the Airbyte platform does -- as a subprocess whose
stdout is a stream of protocol messages -- and counts RECORD messages against
wall-clock time. That is the number that matters: it includes the SAP round
trips, DuckDB, the CDK's serialization and the write to stdout, which is where a
connector actually spends its time.

    ./bin/benchmark.py                       # the default matrix
    ./bin/benchmark.py --case rfc-dd02l-p8   # one case
    ./bin/benchmark.py --repeat 3 --markdown ../docs/performance-raw.md

Needs the same environment as the e2e suite; see bin/test-e2e.sh.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DEFAULT_TABLE = os.environ.get("ERPL_BENCH_TABLE", "DD02L")
MEDIUM_TABLE = os.environ.get("ERPL_BENCH_MEDIUM_TABLE", "SBOOK")


def sap_config() -> dict:
    ashost = os.environ.get("ERPL_SAP_ASHOST")
    if not ashost:
        sys.exit("ERPL_SAP_ASHOST is not set; source your SAP environment first.")
    return {
        "ashost": ashost,
        "sysnr": os.environ.get("ERPL_SAP_SYSNR", "00"),
        "client": os.environ.get("ERPL_SAP_CLIENT", "001"),
        "user": os.environ.get("ERPL_SAP_USER", "DEVELOPER"),
        "password": os.environ.get("ERPL_SAP_PASSWORD", ""),
        "lang": os.environ.get("ERPL_SAP_LANG", "EN"),
    }


@dataclass(frozen=True)
class Case:
    key: str
    title: str
    config: dict
    stream: str
    note: str = ""


@dataclass
class Result:
    case: Case
    records: int = 0
    seconds: float = 0.0
    peak_rss_mb: float = 0.0
    bytes_out: int = 0
    runs: list[float] = field(default_factory=list)

    @property
    def rows_per_second(self) -> float:
        return self.records / self.seconds if self.seconds else 0.0

    @property
    def mb_per_second(self) -> float:
        return (self.bytes_out / 1_048_576) / self.seconds if self.seconds else 0.0


def rfc_case(key: str, title: str, table: str, note: str = "", **overrides) -> Case:
    return Case(
        key=key,
        title=title,
        stream=table,
        note=note,
        config={
            **sap_config(),
            "concurrency": overrides.pop("concurrency", 1),
            "protocol": {
                "mode": "rfc",
                "table_pattern": table,
                "objects": [{"name": table, **overrides}],
            },
        },
    )


def build_matrix() -> list[Case]:
    cases = [
        rfc_case(
            "rfc-serial",
            f"RFC {DEFAULT_TABLE}, serial",
            DEFAULT_TABLE,
            "baseline: one RFC_READ_TABLE call chain",
            partitions=0,
        ),
        rfc_case("rfc-p2", f"RFC {DEFAULT_TABLE}, 2 partitions", DEFAULT_TABLE, partitions=2),
        rfc_case("rfc-p4", f"RFC {DEFAULT_TABLE}, 4 partitions", DEFAULT_TABLE, partitions=4),
        rfc_case("rfc-p8", f"RFC {DEFAULT_TABLE}, 8 partitions", DEFAULT_TABLE, partitions=8),
        rfc_case("rfc-p16", f"RFC {DEFAULT_TABLE}, 16 partitions", DEFAULT_TABLE, partitions=16),
        rfc_case(
            "rfc-projection",
            f"RFC {DEFAULT_TABLE}, 2 of N columns, serial",
            DEFAULT_TABLE,
            "differs from the serial baseline in the projection alone",
            partitions=0,
            columns=["TABNAME", "TABCLASS"],
        ),
        rfc_case(
            "rfc-projection-p8",
            f"RFC {DEFAULT_TABLE}, 2 of N columns, 8 partitions",
            DEFAULT_TABLE,
            "narrow extracts are the regime where partitioning pays",
            partitions=8,
            columns=["TABNAME", "TABCLASS"],
        ),
        rfc_case("rfc-medium", f"RFC {MEDIUM_TABLE}, 8 partitions", MEDIUM_TABLE, "wider rows", partitions=8),
    ]
    odp_context = os.environ.get("ERPL_SAP_ODP_CONTEXT")
    odp_name = os.environ.get("ERPL_SAP_ODP_NAME")
    if odp_context and odp_name:
        for threads in (1, 4, 8):
            cases.append(
                Case(
                    key=f"odp-full-t{threads}",
                    title=f"ODP full {odp_name}, {threads} thread(s)",
                    stream=f"{odp_context}/{odp_name}",
                    config={
                        **sap_config(),
                        "concurrency": 1,
                        "protocol": {
                            "mode": "odp_rfc",
                            "context": odp_context,
                            "threads": threads,
                            "objects": [{"name": odp_name, "context": odp_context}],
                        },
                    },
                )
            )
    odata_url = os.environ.get("ERPL_SAP_ODP_ODATA_URL")
    if odata_url:
        cases.append(
            Case(
                key="odp-odata",
                title="ODP over OData, initial load",
                stream=odata_url.rstrip("/").rsplit("/", 1)[-1],
                config={
                    "client": sap_config()["client"],
                    "user": sap_config()["user"],
                    "password": sap_config()["password"],
                    "base_url": os.environ.get("ERPL_SAP_BASE_URL", ""),
                    "concurrency": 1,
                    "protocol": {"mode": "odp_odata", "objects": [{"url": odata_url}]},
                },
            )
        )
    return cases


def discover_schema(case: Case, workdir: Path) -> dict:
    messages = run_connector(case, "discover", workdir)[0]
    catalogs = [m["catalog"] for m in messages if m.get("type") == "CATALOG"]
    if not catalogs:
        raise RuntimeError(f"{case.key}: discover produced no catalog")
    streams = {s["name"]: s for s in catalogs[0]["streams"]}
    if case.stream not in streams:
        raise RuntimeError(f"{case.key}: {case.stream} not in {sorted(streams)}")
    return streams[case.stream]["json_schema"]


def run_connector(case: Case, command: str, workdir: Path, catalog: dict | None = None):
    config_path = workdir / "config.json"
    config_path.write_text(json.dumps(case.config))
    args = [sys.executable, "-m", "source_sap.run", command, "--config", str(config_path)]
    if catalog is not None:
        catalog_path = workdir / "catalog.json"
        catalog_path.write_text(json.dumps(catalog))
        args += ["--catalog", str(catalog_path)]

    # `getrusage(RUSAGE_CHILDREN).ru_maxrss` is a high-water mark across every
    # child the process has ever reaped, so it only ever climbs and cannot
    # attribute memory to one case. Sample the child's own VmHWM instead.
    start = time.perf_counter()
    proc, peak_kb = _run_and_watch_rss(args)
    elapsed = time.perf_counter() - start

    messages = []
    for line in proc.stdout.splitlines():
        if line.startswith("{"):
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    if proc.returncode != 0:
        raise RuntimeError(f"{case.key} {command} exited {proc.returncode}: {proc.stderr[-2000:]}")
    return messages, elapsed, peak_kb / 1024, len(proc.stdout)


def _run_and_watch_rss(args: list[str]) -> tuple[subprocess.CompletedProcess, float]:
    """Run a child and return it together with its own peak RSS in KiB.

    `VmHWM` is the kernel's high-water mark for that one process, which is
    exactly what is wanted -- but it vanishes when the process exits, hence the
    sampler thread.
    """
    peak = 0.0

    def sample(pid: int, stop: threading.Event) -> None:
        nonlocal peak
        status = pathlib.Path(f"/proc/{pid}/status")
        while not stop.wait(0.05):
            try:
                for line in status.read_text().splitlines():
                    if line.startswith("VmHWM:"):
                        peak = max(peak, float(line.split()[1]))
                        break
            except (OSError, ValueError, IndexError):
                return  # the child is gone

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=HERE)
    stop = threading.Event()
    watcher = threading.Thread(target=sample, args=(process.pid, stop), daemon=True)
    watcher.start()
    try:
        stdout, stderr = process.communicate(timeout=3600)
    except subprocess.TimeoutExpired:
        # Left running, it would compete with every later case for the same SAP
        # system and quietly poison the rest of the matrix.
        process.kill()
        stdout, stderr = process.communicate()
        raise
    finally:
        stop.set()
        watcher.join(timeout=1)
    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr), peak


def assert_quiet_system() -> None:
    """Refuse to measure while something else is using the same SAP system.

    The first run of this matrix reported a 17x *slowdown* from partitioning,
    because the e2e suite was hammering the same trial system throughout the
    partitioned cases while the serial baseline had run before it started. A
    benchmark that silently measures contention is worse than no benchmark.
    """
    own = {os.getpid(), os.getppid()}
    busy = []
    for proc_dir in pathlib.Path("/proc").iterdir():
        if not proc_dir.name.isdigit() or int(proc_dir.name) in own:
            continue
        try:
            cmdline = (proc_dir / "cmdline").read_bytes().decode(errors="replace")
        except OSError:
            continue
        readable = cmdline.replace("\0", " ").strip()
        if "benchmark.py" in readable:
            continue
        # Deliberately broad. A false positive costs one --allow-busy; a false
        # negative costs a table of numbers that look like throughput and are
        # contention, which is how this check came to exist. An earlier edit
        # narrowed it to two pytest paths and missed ./bin/test-e2e.sh.
        if re.search(r"source_sap|pytest|test-e2e|trace-round-trips|airbyte", readable):
            busy.append(f"  pid {proc_dir.name}: {readable[:100]}")
    if busy:
        sys.exit(
            "Something else is talking to SAP, so this would measure contention "
            "rather than throughput:\n"
            + "\n".join(busy)
            + "\nWait for it to finish, or pass --allow-busy to measure anyway."
        )


def measure(case: Case, repeat: int, workdir: Path) -> Result:
    schema = discover_schema(case, workdir)
    catalog = {
        "streams": [
            {
                "stream": {"name": case.stream, "json_schema": schema, "supported_sync_modes": ["full_refresh"]},
                "sync_mode": "full_refresh",
                "destination_sync_mode": "overwrite",
            }
        ]
    }
    result = Result(case=case)
    # Every figure for a case comes from one run: pairing a record count from one
    # attempt with a duration from another is how a harness reports a rate that
    # never happened.
    best = None
    for attempt in range(repeat):
        messages, elapsed, rss_mb, out_bytes = run_connector(case, "read", workdir, catalog)
        records = sum(1 for m in messages if m.get("type") == "RECORD")
        errors = [m for m in messages if m.get("type") == "TRACE" and m.get("trace", {}).get("type") == "ERROR"]
        if errors:
            raise RuntimeError(f"{case.key}: {errors[0]['trace']['error']['message']}")
        result.runs.append(elapsed)
        if best is None or elapsed < best[0]:
            best = (elapsed, records, rss_mb, out_bytes)
        print(
            f"    run {attempt + 1}/{repeat}: {records:,} records in {elapsed:.1f}s ({records / elapsed:,.0f} rec/s)",
            flush=True,
        )
    result.seconds, result.records, result.peak_rss_mb, result.bytes_out = best
    return result


def render_markdown(results: list[Result], repeat: int, failures: list[tuple[Case, str]] | None = None) -> str:
    import platform

    lines = [
        "# Replication performance: measured figures",
        "",
        "Measured end to end: the connector runs as a subprocess, exactly as the Airbyte",
        "platform runs it, and RECORD messages are counted against wall-clock time. The",
        "figures therefore include the SAP round trips, DuckDB, the CDK's serialization",
        "and the write to stdout — not just the extraction.",
        "",
        f"Best of {repeat} run(s) per case. Generated by `bin/benchmark.py`.",
        "",
        "| Case | Records | Time | Records/s | MB/s | Peak RSS |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r.case.title} | {r.records:,} | {r.seconds:.1f}s | "
            f"{r.rows_per_second:,.0f} | {r.mb_per_second:.1f} | {r.peak_rss_mb:,.0f} MB |"
        )
    baseline = next((r for r in results if r.case.key == "rfc-serial"), None)
    if baseline and baseline.rows_per_second:
        lines += [
            "",
            "## Effect of partitioning",
            "",
            "| Partitions | Records/s | Speed-up vs serial |",
            "|---:|---:|---:|",
        ]
        for key, label in (
            ("rfc-serial", "0 (serial)"),
            ("rfc-p2", "2"),
            ("rfc-p4", "4"),
            ("rfc-p8", "8"),
            ("rfc-p16", "16"),
        ):
            r = next((x for x in results if x.case.key == key), None)
            if r:
                lines.append(
                    f"| {label} | {r.rows_per_second:,.0f} | {r.rows_per_second / baseline.rows_per_second:.2f}x |"
                )
    if failures:
        lines += [
            "",
            "## Cases that failed",
            "",
            "These produced no measurement. The table above is therefore not a",
            "complete picture of this run.",
            "",
            "| Case | Error |",
            "|---|---|",
        ]
        lines += [f"| {case.title} | {error} |" for case, error in failures]

    notes = [f"- **{r.case.title}** — {r.case.note}" for r in results if r.case.note]
    if notes:
        lines += ["", "## Notes", ""] + notes
    lines += [
        "",
        "## Environment",
        "",
        f"- Host: {platform.platform()}, {os.cpu_count()} CPUs",
        f"- Python {platform.python_version()}",
        f"- SAP: {os.environ.get('ERPL_SAP_ASHOST')} client {os.environ.get('ERPL_SAP_CLIENT', '001')}",
        "",
        "The SAP system here is a single-container ABAP trial sharing a laptop with the",
        "connector, so these are *relative* figures for comparing settings, not a",
        "capacity statement about production hardware.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", help="run only these case keys")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument(
        "--markdown",
        type=Path,
        default=Path("../docs/performance-raw.md"),
        help="where to write the measured table (default: docs/performance-raw.md). "
        "docs/performance.md is hand-written prose citing it, and is never generated.",
    )
    parser.add_argument("--list", action="store_true", help="list the cases and exit")
    parser.add_argument("--allow-busy", action="store_true", help="measure even if something else is using SAP")
    args = parser.parse_args()

    if not args.list and not args.allow_busy:
        assert_quiet_system()

    cases = build_matrix()
    if args.list:
        for case in cases:
            print(f"{case.key:20s} {case.title}")
        return 0
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c.key in wanted]
        if not cases:
            sys.exit(f"no case matched {sorted(wanted)}")

    workdir = Path(os.environ.get("TMPDIR", "/tmp")) / "source-sap-bench"
    workdir.mkdir(parents=True, exist_ok=True)

    results: list[Result] = []
    failures: list[tuple[Case, str]] = []
    for case in cases:
        print(f"  {case.key}: {case.title}", flush=True)
        try:
            results.append(measure(case, args.repeat, workdir))
        except Exception as exc:  # one bad case must not lose the rest
            print(f"    FAILED: {exc}", flush=True)
            # Recorded, not dropped: a report that silently omits what failed
            # reads as a complete picture of a run that was not.
            failures.append((case, str(exc).splitlines()[0] if str(exc) else repr(exc)))

    if not results:
        return 1
    report = render_markdown(results, args.repeat, failures)
    print("\n" + report)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(report)
        print(f"written to {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
