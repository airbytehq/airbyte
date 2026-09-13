"""DuckDB/ERPL session construction."""

import pytest

from source_sap.session import MAX_DUCKDB_THREADS, ErplSession, SapRfcCredentials, SessionSettings


class TestSapRfcCredentials:
    def test_direct_connection_fields(self):
        creds = SapRfcCredentials.from_config(
            {"ashost": "sap.example.com", "sysnr": "00", "client": "100", "user": "u", "password": "p", "lang": "EN"}
        )
        sql, params = creds.create_secret_sql("sap")
        assert "CREATE OR REPLACE SECRET" in sql
        assert "TYPE sap_rfc" in sql
        # Every value must travel as a bound parameter, never interpolated.
        assert "sap.example.com" not in sql
        assert "p" not in [c for c in sql if c.islower()] or "PASSWD" in sql
        assert params["ashost"] == "sap.example.com"
        assert params["passwd"] == "p"

    def test_password_is_never_interpolated_into_sql(self):
        creds = SapRfcCredentials.from_config(
            {"ashost": "h", "sysnr": "00", "client": "100", "user": "u", "password": "'; DROP TABLE x; --"}
        )
        sql, params = creds.create_secret_sql("sap")
        assert "DROP TABLE" not in sql
        assert params["passwd"] == "'; DROP TABLE x; --"

    def test_load_balanced_connection(self):
        creds = SapRfcCredentials.from_config(
            {
                "mshost": "ms.example.com",
                "sysid": "PRD",
                "group": "PUBLIC",
                "client": "100",
                "user": "u",
                "password": "p",
            }
        )
        _, params = creds.create_secret_sql("sap")
        assert params["mshost"] == "ms.example.com"
        assert params["sysid"] == "PRD"
        assert "ashost" not in params

    def test_optional_fields_are_omitted_not_blank(self):
        creds = SapRfcCredentials.from_config(
            {"ashost": "h", "sysnr": "00", "client": "100", "user": "u", "password": "p", "saprouter": ""}
        )
        _, params = creds.create_secret_sql("sap")
        assert "saprouter" not in params
        assert "lang" not in params

    def test_snc_fields_survive(self):
        creds = SapRfcCredentials.from_config(
            {
                "ashost": "h",
                "sysnr": "00",
                "client": "100",
                "user": "u",
                "snc_mode": "1",
                "snc_partnername": "p:CN=SAP",
                "snc_lib": "/usr/lib/lib.so",
            }
        )
        _, params = creds.create_secret_sql("sap")
        assert params["snc_mode"] == "1"
        assert "passwd" not in params  # SNC logon needs no password

    def test_missing_host_is_a_config_error(self):
        from source_sap.errors import config_error

        with pytest.raises(Exception) as exc:
            SapRfcCredentials.from_config({"client": "100", "user": "u", "password": "p"})
        assert "ashost" in str(exc.value) or "mshost" in str(exc.value)
        assert config_error  # imported symbol exists


class TestSessionSettings:
    """The thread budget is the connector's single largest throughput setting.

    Each DuckDB thread here is a blocking RFC call, not CPU work: measured on a
    55-column, 164,673-row table, throughput rises near-linearly with the budget
    (1 thread 1,479 rows/s, 8 threads 8,740, 16 threads 11,720, 32 threads
    12,919). It used to be divided by the Airbyte worker count on the grounds of
    not oversubscribing -- but every stream shares ONE DuckDB instance, whose
    scheduler already shares its threads across concurrent queries, so the
    division only starved the process: a single-stream sync measured 3.9x slower
    at `concurrency: 16` than at 1, for a setting documented as how many streams
    run in parallel.
    """

    def test_the_budget_is_not_divided_by_the_worker_count(self):
        assert SessionSettings(num_workers=16, cpu_count=16).duckdb_threads == 16
        assert SessionSettings(num_workers=1, cpu_count=16).duckdb_threads == 16

    def test_a_small_machine_gets_its_own_cpu_count(self):
        assert SessionSettings(num_workers=4, cpu_count=4).duckdb_threads == 4

    def test_the_budget_is_capped(self):
        # Past ~16 concurrent RFC calls the gain is small and the SAP-side cost
        # is not: erpl caches at most 16 RFC connections itself.
        assert SessionSettings(num_workers=4, cpu_count=128).duckdb_threads == MAX_DUCKDB_THREADS
        assert MAX_DUCKDB_THREADS == 16

    def test_never_fewer_than_one_duckdb_thread(self):
        assert SessionSettings(num_workers=32, cpu_count=0).duckdb_threads == 1


class TestErplSessionSql:
    def test_extensions_are_loaded_never_installed(self):
        # Extensions are baked into the image; a sync must not reach out to get.erpl.io.
        stmts = ErplSession.bootstrap_statements(("erpl_rfc", "erpl_web"))
        joined = " ".join(stmts)
        assert "INSTALL" not in joined.upper()
        assert "LOAD erpl_rfc" in joined
        assert "erpl_telemetry_enabled" in joined
