"""Realistic-volume syncs against a live SAP system.

The rest of the e2e suite uses SFLIGHT (334 rows), which proves correctness but
says nothing about behaviour at a size anyone would actually replicate. These
run against the DDIC tables the erpl repository itself benchmarks with:

    DD02L   ~165k rows   erpl's own partitioning benchmark table
    SBOOK   ~29k rows    wider rows, a realistic transactional shape
    T100    ~616k rows   only in the "slow" tier

They are marked `slow` and excluded from the default run.
"""

from __future__ import annotations

import os

import pytest

from e2e.conftest import errors, records, run_connector, states

pytestmark = [pytest.mark.requires_creds, pytest.mark.slow]

BENCH_TABLE = os.environ.get("ERPL_BENCH_TABLE", "DD02L")
#: Exactly 40 rows on the ABAP trial, and erpl's own tests assert that literal.
#: A fixed-size table is the one place an exact count is safe to write down.
SMALL_FIXED_TABLE = "/DMO/FLIGHT"
SMALL_FIXED_ROWS = 40
MEDIUM_TABLE = os.environ.get("ERPL_BENCH_MEDIUM_TABLE", "SBOOK")
#: The suite asserts an order of magnitude, not an exact count, because DDIC
#: content differs between systems and grows as objects are created.
MIN_BENCH_ROWS = 100_000

#: The serial-vs-partitioned comparison caps both reads, so this -- not
#: MIN_BENCH_ROWS -- is what a non-empty result looks like there.
VOLUME_ROW_CAP = 50_000
MIN_MEDIUM_ROWS = 10_000


def _config(sap_rfc_config, table, **overrides):
    return {
        **sap_rfc_config,
        "protocol": {
            "mode": "rfc",
            "table_pattern": table,
            "objects": [{"name": table, **overrides}],
        },
    }


def _catalog(stream, schema, sync_mode="full_refresh"):
    return {
        "streams": [
            {
                "stream": {
                    "name": stream,
                    "json_schema": schema,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
                "sync_mode": sync_mode,
                "destination_sync_mode": "overwrite" if sync_mode == "full_refresh" else "append_dedup",
            }
        ]
    }


def _schema(config, tmp_path, name):
    messages = run_connector("discover", config=config, tmp_path=tmp_path)
    catalog = [m["catalog"] for m in messages if m.get("type") == "CATALOG"]
    assert catalog, f"discover produced no catalog: {messages[-2:]}"
    return next(s for s in catalog[0]["streams"] if s["name"] == name)["json_schema"]


class TestLargeTable:
    @pytest.fixture(scope="class")
    def schema(self, sap_rfc_config, tmp_path_factory):
        return _schema(_config(sap_rfc_config, BENCH_TABLE), tmp_path_factory.mktemp("vol"), BENCH_TABLE)

    def test_a_six_figure_table_replicates_completely(self, sap_rfc_config, schema, tmp_path):
        config = _config(sap_rfc_config, BENCH_TABLE, partitions=8)
        messages = run_connector("read", config=config, catalog=_catalog(BENCH_TABLE, schema), tmp_path=tmp_path)
        assert errors(messages) == []
        rows = records(messages, BENCH_TABLE)
        assert len(rows) >= MIN_BENCH_ROWS, (
            f"{BENCH_TABLE} returned {len(rows):,} rows; expected at least {MIN_BENCH_ROWS:,}"
        )

    def test_partitioned_and_serial_reads_agree_at_volume(self, sap_rfc_config, schema, tmp_path):
        """The property that matters for partitioning: same rows, any order.

        A partitioned scan reads independent row windows, so an off-by-one in the
        windowing shows up as duplicated or missing rows -- and only at a size
        where more than one window exists.
        """
        key = ["TABNAME"] if BENCH_TABLE == "DD02L" else None
        serial = run_connector(
            "read",
            config=_config(sap_rfc_config, BENCH_TABLE, partitions=0, columns=key, max_rows=VOLUME_ROW_CAP),
            catalog=_catalog(BENCH_TABLE, schema),
            tmp_path=tmp_path,
        )
        parallel = run_connector(
            "read",
            config=_config(sap_rfc_config, BENCH_TABLE, partitions=8, columns=key, max_rows=VOLUME_ROW_CAP),
            catalog=_catalog(BENCH_TABLE, schema),
            tmp_path=tmp_path,
        )
        assert errors(serial) == [] and errors(parallel) == []

        def keyed(messages):
            return sorted(tuple(sorted(r["data"].items())) for r in records(messages, BENCH_TABLE))

        left, right = keyed(serial), keyed(parallel)
        # Before comparing: two empty results are equal, so a regression that
        # returned nothing at all -- a projection that drops the column, a
        # max_rows fault, a stream-name change that makes records() match
        # nothing -- would otherwise pass this test green.
        assert len(left) == VOLUME_ROW_CAP, (
            f"the serial read returned {len(left):,}, not the {VOLUME_ROW_CAP:,} asked for"
        )
        assert len(left) == len(right), f"serial {len(left):,} vs partitioned {len(right):,}"
        assert left == right

    def test_no_duplicate_rows_at_volume(self, sap_rfc_config, schema, tmp_path):
        config = _config(sap_rfc_config, BENCH_TABLE, partitions=8, columns=["TABNAME"])
        messages = run_connector("read", config=config, catalog=_catalog(BENCH_TABLE, schema), tmp_path=tmp_path)
        assert errors(messages) == []
        names = [r["data"]["TABNAME"] for r in records(messages, BENCH_TABLE)]
        assert len(names) >= MIN_BENCH_ROWS, f"only {len(names):,} rows; nothing was exercised"
        # TABNAME is the key of DD02L, so every value must appear exactly once.
        assert len(names) == len(set(names)), f"{len(names) - len(set(names)):,} duplicate rows in a partitioned scan"

    def test_memory_stays_bounded_at_volume(self, sap_rfc_config, schema, tmp_path):
        """Records are streamed, not accumulated.

        The connector yields from a generator all the way to stdout; if anything
        in that chain materialised the result, a six-figure table would show it.
        """
        import json as _json
        import resource
        import subprocess
        import sys

        before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        config_file = tmp_path / "c.json"
        config_file.write_text(_json.dumps(_config(sap_rfc_config, BENCH_TABLE, partitions=4)))
        catalog_file = tmp_path / "cat.json"
        catalog_file.write_text(_json.dumps(_catalog(BENCH_TABLE, schema)))
        env = dict(os.environ)
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "source_sap.run",
                "read",
                "--config",
                str(config_file),
                "--catalog",
                str(catalog_file),
            ],
            capture_output=True,
            text=True,
            env=env,
            timeout=1800,
        )
        assert proc.returncode == 0, proc.stderr[-2000:]
        peak_mb = max(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss - before, 0) / 1024
        rows = proc.stdout.count('"type":"RECORD"')
        assert rows >= MIN_BENCH_ROWS
        # Generous, because DuckDB and the SAP SDK have their own footprint; the
        # point is that it does not scale with the row count.
        assert peak_mb < 2048, f"peak RSS {peak_mb:,.0f} MB for {rows:,} rows looks like buffering"


class TestMediumTableIncremental:
    @pytest.fixture(scope="class")
    def schema(self, sap_rfc_config, tmp_path_factory):
        return _schema(_config(sap_rfc_config, MEDIUM_TABLE), tmp_path_factory.mktemp("vol2"), MEDIUM_TABLE)

    def test_a_realistic_transactional_table_replicates(self, sap_rfc_config, schema, tmp_path):
        config = _config(sap_rfc_config, MEDIUM_TABLE, partitions=4)
        messages = run_connector("read", config=config, catalog=_catalog(MEDIUM_TABLE, schema), tmp_path=tmp_path)
        assert errors(messages) == []
        rows = records(messages, MEDIUM_TABLE)
        assert len(rows) >= MIN_MEDIUM_ROWS
        # SBOOK carries money, dates and a client field -- the awkward types.
        sample = rows[0]["data"]
        assert "MANDT" in sample and "CARRID" in sample

    def test_incremental_at_volume_narrows_the_second_run(self, sap_rfc_config, schema, tmp_path):
        if MEDIUM_TABLE != "SBOOK":
            pytest.skip("cursor field is SBOOK-specific")
        config = _config(sap_rfc_config, MEDIUM_TABLE, cursor_field="FLDATE", partitions=0)
        catalog = _catalog(MEDIUM_TABLE, schema, "incremental")

        first = run_connector("read", config=config, catalog=catalog, tmp_path=tmp_path)
        assert errors(first) == []
        first_rows = records(first, MEDIUM_TABLE)
        assert len(first_rows) >= MIN_MEDIUM_ROWS
        state = states(first, MEDIUM_TABLE)[-1]
        assert state["stream"]["stream_state"].get("FLDATE")

        second = run_connector("read", config=config, catalog=catalog, state=[state], tmp_path=tmp_path)
        assert errors(second) == []
        second_rows = records(second, MEDIUM_TABLE)
        assert 0 < len(second_rows) < len(first_rows), (
            "an incremental second run should return only the rows at the high-water mark"
        )


class TestPartitioningInvariants:
    """The properties erpl's own partition tests assert, through the connector.

    Row *order* is deliberately never asserted: partitioned workers finish in
    whatever order they finish.
    """

    @pytest.fixture(scope="class")
    def small_schema(self, sap_rfc_config, tmp_path_factory):
        return _schema(_config(sap_rfc_config, SMALL_FIXED_TABLE), tmp_path_factory.mktemp("vol3"), SMALL_FIXED_TABLE)

    def test_more_workers_than_windows_still_returns_every_row(self, sap_rfc_config, small_schema, tmp_path):
        # 40 rows across 8 partitions: most workers get an empty window, and an
        # empty window read as end-of-scan used to truncate the result.
        config = _config(sap_rfc_config, SMALL_FIXED_TABLE, partitions=8)
        messages = run_connector(
            "read", config=config, catalog=_catalog(SMALL_FIXED_TABLE, small_schema), tmp_path=tmp_path
        )
        assert errors(messages) == []
        assert len(records(messages, SMALL_FIXED_TABLE)) == SMALL_FIXED_ROWS

    def test_max_rows_is_scan_wide_not_per_worker(self, sap_rfc_config, tmp_path):
        """4 partitions x MAX_ROWS 5000 must be 5000 rows, not 20000."""
        schema = _schema(_config(sap_rfc_config, BENCH_TABLE), tmp_path, BENCH_TABLE)
        config = _config(sap_rfc_config, BENCH_TABLE, partitions=4, max_rows=5000, columns=["TABNAME"])
        messages = run_connector("read", config=config, catalog=_catalog(BENCH_TABLE, schema), tmp_path=tmp_path)
        assert errors(messages) == []
        assert len(records(messages, BENCH_TABLE)) == 5000

    def test_a_pushed_down_filter_selects_a_strict_minority(self, sap_rfc_config, tmp_path):
        """Without this guard, "filtered equals unfiltered" is satisfiable by
        returning everything, and the filter test proves nothing."""
        schema = _schema(_config(sap_rfc_config, BENCH_TABLE), tmp_path, BENCH_TABLE)
        catalog = _catalog(BENCH_TABLE, schema)
        unfiltered = run_connector(
            "read",
            config=_config(sap_rfc_config, BENCH_TABLE, partitions=8, columns=["TABNAME"]),
            catalog=catalog,
            tmp_path=tmp_path,
        )
        filtered = run_connector(
            "read",
            config=_config(
                sap_rfc_config, BENCH_TABLE, partitions=8, columns=["TABNAME"], filter="TABCLASS = 'TRANSP'"
            ),
            catalog=catalog,
            tmp_path=tmp_path,
        )
        assert errors(unfiltered) == [] and errors(filtered) == []
        total = len(records(unfiltered, BENCH_TABLE))
        kept = len(records(filtered, BENCH_TABLE))
        assert total > MIN_BENCH_ROWS
        assert 0 < kept, "the filter must select something"
        assert kept * 2 < total, (
            "the filter must reject a clear majority, or whole batches never come "
            f"back empty and the test exercises nothing ({kept:,} of {total:,})"
        )


#: ODQ metadata that numbers one extraction's rows, not the rows themselves.
SEQUENCE_COLUMNS = frozenset({"ODQ_TSN", "ODQ_RECORDNO", "ODQ_UNITNO", "ODQ_ENTITYCNTR"})


class TestOdpVolume:
    """ODP at a size where more than one package is fetched."""

    ODP_CONTEXT = os.environ.get("ERPL_SAP_ODP_VOLUME_CONTEXT", "ABAP_CDS")
    ODP_NAME = os.environ.get("ERPL_SAP_ODP_VOLUME_NAME", "SEPM_ISOI$P")
    MIN_ODP_ROWS = 20_000

    def _config(self, sap_rfc_config, **overrides):
        return {
            **sap_rfc_config,
            "protocol": {
                "mode": "odp_rfc",
                "context": self.ODP_CONTEXT,
                "objects": [{"name": self.ODP_NAME, "context": self.ODP_CONTEXT, **overrides}],
            },
        }

    @property
    def stream(self):
        return f"{self.ODP_CONTEXT}/{self.ODP_NAME}"

    @pytest.fixture(scope="class")
    def schema(self, sap_rfc_config, tmp_path_factory):
        config = self._config(sap_rfc_config)
        messages = run_connector("discover", config=config, tmp_path=tmp_path_factory.mktemp("odpvol"))
        catalogs = [m["catalog"] for m in messages if m.get("type") == "CATALOG"]
        if not catalogs or not catalogs[0]["streams"]:
            pytest.skip(f"{self.stream} is not available on this system")
        return catalogs[0]["streams"][0]["json_schema"]

    def test_a_multi_package_full_extract_is_complete(self, sap_rfc_config, schema, tmp_path):
        messages = run_connector(
            "read",
            config=self._config(sap_rfc_config, threads=1),
            catalog=_catalog(self.stream, schema),
            tmp_path=tmp_path,
        )
        assert errors(messages) == []
        assert len(records(messages, self.stream)) >= self.MIN_ODP_ROWS

    def test_parallel_and_serial_extracts_agree(self, sap_rfc_config, schema, tmp_path):
        """Parallel package fetch racing into an under-count is the ODP failure
        mode; a serial read is the reference."""
        catalog = _catalog(self.stream, schema)
        serial = run_connector(
            "read", config=self._config(sap_rfc_config, threads=1), catalog=catalog, tmp_path=tmp_path
        )
        parallel = run_connector(
            "read", config=self._config(sap_rfc_config, threads=8), catalog=catalog, tmp_path=tmp_path
        )
        assert errors(serial) == [] and errors(parallel) == []

        def keyed(messages):
            # Without the ODQ sequence columns. ODQ_TSN is the transaction
            # sequence number of the *extraction*, and ODQ_RECORDNO / ODQ_UNITNO
            # / ODQ_ENTITYCNTR number the rows within it, so two extractions of
            # identical data differ in all four by design. Comparing them
            # compares the request, not the data. ODQ_CHANGEMODE is data -- it
            # says what happened to the row -- and stays in.
            return sorted(
                tuple(sorted((k, v) for k, v in r["data"].items() if k not in SEQUENCE_COLUMNS))
                for r in records(messages, self.stream)
            )

        left, right = keyed(serial), keyed(parallel)
        assert len(left) >= self.MIN_ODP_ROWS
        # Comparing sorted multisets catches a dropped package, a duplicated one
        # and a corrupted value in one assertion, whatever the absolute count.
        assert len(left) == len(right), f"serial {len(left):,} vs 8 threads {len(right):,}"
        assert left == right

    def test_no_rows_are_duplicated_across_packages(self, sap_rfc_config, schema, tmp_path):
        messages = run_connector(
            "read",
            config=self._config(sap_rfc_config, threads=8),
            catalog=_catalog(self.stream, schema),
            tmp_path=tmp_path,
        )
        # On the business columns only: ODQ_RECORDNO and ODQ_UNITNO number the
        # rows of one extraction, so a row delivered twice in two packages would
        # carry two different numbers and this assertion could never fail.
        rows = [
            tuple(sorted((k, v) for k, v in r["data"].items() if k not in SEQUENCE_COLUMNS))
            for r in records(messages, self.stream)
        ]
        assert len(rows) == len(set(rows)), f"{len(rows) - len(set(rows)):,} duplicate rows across ODP packages"
