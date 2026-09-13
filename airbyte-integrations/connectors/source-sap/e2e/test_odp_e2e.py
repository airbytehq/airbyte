"""End-to-end ODP syncs -- RFC and OData flavours -- against a live SAP system."""

from __future__ import annotations

import pytest

from e2e.conftest import errors, records, run_connector, states
from source_sap.streams import CDC_DELETED_AT

pytestmark = pytest.mark.requires_creds


def _catalog(stream: str, schema: dict, sync_mode: str = "full_refresh"):
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


def _discover(config, tmp_path, name=None):
    messages = run_connector("discover", config=config, tmp_path=tmp_path)
    catalog = [m["catalog"] for m in messages if m.get("type") == "CATALOG"]
    assert catalog, f"discover produced no catalog: {messages[-3:]}"
    streams = catalog[0]["streams"]
    stream = next((s for s in streams if s["name"] == name), streams[0]) if streams else None
    assert stream is not None
    return stream


SUBSCRIBER_PROCESS = "AB_E2E_ODP_RFC"


@pytest.fixture
def fresh_odp_subscription(sap_rfc_config, odp_target, erpl_extensions):
    """Drop the server-side ODP subscription so each delta test starts at DELTAINIT.

    The delta pointer lives on SAP, not in the test process, so without this a
    second run of the suite sees an already-initialised subscription and gets
    zero rows where it expects a snapshot.
    """
    import duckdb

    context, name = odp_target
    con = duckdb.connect(config={"allow_unsigned_extensions": "true", "extension_directory": erpl_extensions})
    try:
        for ext in ("erpl_rfc", "erpl_odp"):
            con.load_extension(ext)
        con.execute("SET erpl_telemetry_enabled = false")
        con.execute(
            "CREATE OR REPLACE SECRET t (TYPE sap_rfc, ASHOST $h, SYSNR $n, CLIENT $c, USER $u, PASSWD $p, LANG $l)",
            {
                "h": sap_rfc_config["ashost"],
                "n": sap_rfc_config["sysnr"],
                "c": sap_rfc_config["client"],
                "u": sap_rfc_config["user"],
                "p": sap_rfc_config["password"],
                "l": sap_rfc_config["lang"],
            },
        )
        for pragma in (
            f"PRAGMA sap_odp_close_delta_cursor('{context}', '{SUBSCRIBER_PROCESS}', '{name}')",
            f"PRAGMA sap_odp_drop('{context}', 'ERPL', '{SUBSCRIBER_PROCESS}', '{name}')",
        ):
            try:
                con.execute(pragma).fetchall()
            except Exception:
                pass  # nothing to clean up on a first run
    finally:
        con.close()
    yield


class TestOdpRfc:
    @pytest.fixture(scope="class")
    def config(self, sap_rfc_config, odp_target):
        context, name = odp_target
        return {
            **sap_rfc_config,
            "protocol": {
                "mode": "odp_rfc",
                "context": context,
                "objects": [{"name": name, "context": context, "subscriber_process": SUBSCRIBER_PROCESS}],
            },
        }

    def test_check_lists_the_odp_contexts(self, config, tmp_path):
        messages = run_connector("check", config=config, tmp_path=tmp_path)
        status = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert status and status[0]["connectionStatus"]["status"] == "SUCCEEDED"

    def test_discover_reports_delta_support_and_a_key(self, config, tmp_path, odp_target):
        context, name = odp_target
        stream = _discover(config, tmp_path, f"{context}/{name}")
        assert "incremental" in stream["supported_sync_modes"]
        assert stream["source_defined_primary_key"]
        # The ODP control columns must be in the schema; they arrive in the data.
        assert "ODQ_CHANGEMODE" in stream["json_schema"]["properties"]
        # And the tombstone the connector derives from them: a destination that
        # never sees it in the catalog has no way to apply a delete.
        assert CDC_DELETED_AT in stream["json_schema"]["properties"]

    def test_full_refresh_reads_the_snapshot(self, config, tmp_path, odp_target):
        context, name = odp_target
        stream_name = f"{context}/{name}"
        stream = _discover(config, tmp_path, stream_name)
        messages = run_connector(
            "read", config=config, catalog=_catalog(stream_name, stream["json_schema"]), tmp_path=tmp_path
        )
        assert errors(messages) == []
        assert len(records(messages, stream_name)) > 0

    def test_delta_returns_a_snapshot_then_nothing(self, config, tmp_path, odp_target, fresh_odp_subscription):
        """The defining ODP behaviour: DELTAINIT, then only changes."""
        context, name = odp_target
        stream_name = f"{context}/{name}"
        stream = _discover(config, tmp_path, stream_name)
        catalog = _catalog(stream_name, stream["json_schema"], "incremental")

        first = run_connector("read", config=config, catalog=catalog, tmp_path=tmp_path)
        assert errors(first) == []
        first_rows = records(first, stream_name)
        assert len(first_rows) > 0, "the DELTAINIT run must return the current snapshot"

        state = states(first, stream_name)[-1]
        blob = state["stream"]["stream_state"]
        # The whole client-side state is the subscriber process; the pointer is on SAP.
        assert blob["subscriber_process"] == SUBSCRIBER_PROCESS
        assert blob["initialized"] is True

        second = run_connector("read", config=config, catalog=catalog, state=[state], tmp_path=tmp_path)
        assert errors(second) == []
        assert len(records(second, stream_name)) == 0, "a second delta run must return no changes"

    def test_the_delta_cursor_is_released_after_the_first_run(
        self, config, tmp_path, odp_target, fresh_odp_subscription, erpl_extensions, sap_rfc_config
    ):
        """A DELTAINIT leaves a cursor open on SAP unless the connector closes it.

        `on_success` runs before `next_state`, so on the very first incremental
        run the Airbyte state blob is still empty -- the cleanup has to fall back
        to the name the read used.
        """
        import duckdb

        context, name = odp_target
        stream_name = f"{context}/{name}"
        stream = _discover(config, tmp_path, stream_name)
        messages = run_connector(
            "read",
            config=config,
            catalog=_catalog(stream_name, stream["json_schema"], "incremental"),
            tmp_path=tmp_path,
        )
        assert errors(messages) == []

        con = duckdb.connect(config={"allow_unsigned_extensions": "true", "extension_directory": erpl_extensions})
        try:
            for ext in ("erpl_rfc", "erpl_odp"):
                con.load_extension(ext)
            con.execute("SET erpl_telemetry_enabled = false")
            con.execute(
                "CREATE OR REPLACE SECRET t (TYPE sap_rfc, ASHOST $h, SYSNR $n, CLIENT $c, "
                "USER $u, PASSWD $p, LANG $l)",
                {
                    "h": sap_rfc_config["ashost"],
                    "n": sap_rfc_config["sysnr"],
                    "c": sap_rfc_config["client"],
                    "u": sap_rfc_config["user"],
                    "p": sap_rfc_config["password"],
                    "l": sap_rfc_config["lang"],
                },
            )
            open_cursors = con.execute(
                "SELECT count(*) FROM sap_odp_show_cursors() WHERE subscriber_proc = ? AND NOT is_closed",
                [SUBSCRIBER_PROCESS],
            ).fetchone()[0]
        finally:
            con.close()
        assert open_cursors == 0, "the connector left a delta cursor reserved on SAP after the first run"

    def test_a_failed_delta_read_still_releases_the_cursor(self, config, tmp_path, odp_target, fresh_odp_subscription):
        """The failure path owes SAP its cursor back, even owing no checkpoint.

        Deliberately not asserted as "zero open cursors": SAP refuses to close a
        cursor left mid-fetch, so a green assertion there would depend on where
        the failure happened to land. What changed, and what is asserted, is that
        the connector attempts the release at all -- before this it was reachable
        only through `on_success`, which a failed stream never reaches.
        """
        context, name = odp_target
        stream_name = f"{context}/{name}"
        stream = _discover(config, tmp_path, stream_name)
        broken = {
            **config,
            "protocol": {
                **config["protocol"],
                "objects": [{"name": name, "context": context, "columns": ["NO_SUCH_COLUMN_XYZ"]}],
            },
        }
        messages = run_connector(
            "read",
            config=broken,
            catalog=_catalog(stream_name, stream["json_schema"], "incremental"),
            tmp_path=tmp_path,
        )
        assert errors(messages), "the projection names a column SAP does not have; the read must fail"
        logs = " ".join(m.get("log", {}).get("message", "") for m in messages if m.get("type") == "LOG")
        assert "Releasing SAP-side resources" in logs, (
            "a failed delta read must still hand the ODP cursor back; it did not try"
        )
        assert "Not checkpointing" in logs, "and it must still refuse to advance the position"

    def test_an_unchanged_source_is_skipped_without_opening_a_cursor(
        self,
        config,
        tmp_path,
        odp_target,
        fresh_odp_subscription,
        erpl_extensions,
        sap_rfc_config,
    ):
        """A quiet stream should cost one probe, not a delta extraction.

        `sap_odp_get_last_modified` answers without fetching rows; opening a
        delta cursor to discover there is nothing to fetch costs a subscription
        round trip and leaves a cursor to close.
        """
        import duckdb

        context, name = odp_target
        stream_name = f"{context}/{name}"
        stream = _discover(config, tmp_path, stream_name)
        catalog = _catalog(stream_name, stream["json_schema"], "incremental")

        first = run_connector("read", config=config, catalog=catalog, tmp_path=tmp_path)
        assert errors(first) == []
        state = states(first, stream_name)[-1]
        assert state["stream"]["stream_state"].get("last_modified"), (
            "the first run must record the source's last-modified timestamp"
        )

        second = run_connector("read", config=config, catalog=catalog, state=[state], tmp_path=tmp_path)
        assert errors(second) == []
        assert records(second, stream_name) == []
        assert any("skipping the delta read" in str(m.get("log", {}).get("message", "")) for m in second), (
            "the second run should have skipped rather than extracted"
        )
        # The skipped run must still checkpoint, or the next sync looks like a reset.
        assert states(second, stream_name)[-1]["stream"]["stream_state"]["subscriber_process"]

        con = duckdb.connect(config={"allow_unsigned_extensions": "true", "extension_directory": erpl_extensions})
        try:
            for ext in ("erpl_rfc", "erpl_odp"):
                con.load_extension(ext)
            con.execute("SET erpl_telemetry_enabled = false")
            con.execute(
                "CREATE OR REPLACE SECRET t (TYPE sap_rfc, ASHOST $h, SYSNR $n, CLIENT $c, "
                "USER $u, PASSWD $p, LANG $l)",
                {
                    "h": sap_rfc_config["ashost"],
                    "n": sap_rfc_config["sysnr"],
                    "c": sap_rfc_config["client"],
                    "u": sap_rfc_config["user"],
                    "p": sap_rfc_config["password"],
                    "l": sap_rfc_config["lang"],
                },
            )
            open_cursors = con.execute(
                "SELECT count(*) FROM sap_odp_show_cursors() WHERE subscriber_proc = ? AND NOT is_closed",
                [SUBSCRIBER_PROCESS],
            ).fetchone()[0]
        finally:
            con.close()
        assert open_cursors == 0

    def test_delta_records_carry_a_cdc_tombstone_column(self, config, tmp_path, odp_target, fresh_odp_subscription):
        context, name = odp_target
        stream_name = f"{context}/{name}"
        stream = _discover(config, tmp_path, stream_name)
        messages = run_connector(
            "read",
            config=config,
            catalog=_catalog(stream_name, stream["json_schema"], "incremental"),
            tmp_path=tmp_path,
        )
        rows = records(messages, stream_name)
        assert rows
        # The CDK serializes records with omit_none, so a null tombstone is dropped
        # from the payload. Initial-load rows are upserts, so none must carry one.
        assert all(r["data"].get("_ab_cdc_deleted_at") is None for r in rows)
        # The ODP control columns that do have values come through.
        assert "ODQ_TSN" in rows[0]["data"]


class TestOdpODataE2E:
    @pytest.fixture(scope="class")
    def config(self, sap_rfc_config, sap_base_url, odp_odata_url):
        return {
            "client": sap_rfc_config["client"],
            "user": sap_rfc_config["user"],
            "password": sap_rfc_config["password"],
            "base_url": sap_base_url,
            "concurrency": 1,
            "protocol": {"mode": "odp_odata", "objects": [{"url": odp_odata_url}]},
        }

    def test_check_reaches_the_gateway(self, config, tmp_path):
        messages = run_connector("check", config=config, tmp_path=tmp_path)
        status = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert status and status[0]["connectionStatus"]["status"] == "SUCCEEDED"

    def test_check_fails_on_a_bad_password(self, config, tmp_path):
        messages = run_connector("check", config={**config, "password": "nope"}, tmp_path=tmp_path)
        status = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert status and status[0]["connectionStatus"]["status"] == "FAILED"

    def test_discover_infers_the_entity_set_schema(self, config, tmp_path):
        stream = _discover(config, tmp_path)
        assert "incremental" in stream["supported_sync_modes"]
        assert stream["json_schema"]["properties"]
        assert CDC_DELETED_AT in stream["json_schema"]["properties"], (
            "ODP over OData reports deletes the same way ODP over RFC does, so the "
            "catalog has to declare the same tombstone column"
        )

    def test_full_refresh_reads_the_entity_set(self, config, tmp_path):
        stream = _discover(config, tmp_path)
        messages = run_connector(
            "read", config=config, catalog=_catalog(stream["name"], stream["json_schema"]), tmp_path=tmp_path
        )
        assert errors(messages) == []
        assert len(records(messages, stream["name"])) > 0

    def test_delta_resumes_from_the_token_in_airbyte_state(self, config, tmp_path):
        """The DuckDB file is scratch; Airbyte state must carry the whole position."""
        stream = _discover(config, tmp_path)
        catalog = _catalog(stream["name"], stream["json_schema"], "incremental")

        first = run_connector("read", config=config, catalog=catalog, tmp_path=tmp_path)
        assert errors(first) == []
        assert len(records(first, stream["name"])) > 0

        state = states(first, stream["name"])[-1]
        token = state["stream"]["stream_state"].get("delta_token")
        assert token, "the first run must checkpoint a delta token"

        # A fresh process gets a brand-new DuckDB file, so this only works if the
        # token in Airbyte state is enough to restore erpl_web's subscription.
        second = run_connector("read", config=config, catalog=catalog, state=[state], tmp_path=tmp_path)
        assert errors(second) == []
        assert len(records(second, stream["name"])) == 0

    def test_full_refresh_ignores_a_stored_token(self, config, tmp_path):
        stream = _discover(config, tmp_path)
        incremental = _catalog(stream["name"], stream["json_schema"], "incremental")
        first = run_connector("read", config=config, catalog=incremental, tmp_path=tmp_path)
        state = states(first, stream["name"])[-1]

        full = run_connector(
            "read",
            config=config,
            catalog=_catalog(stream["name"], stream["json_schema"]),
            state=[state],
            tmp_path=tmp_path,
        )
        assert errors(full) == []
        # force_full_load must override the stored position.
        assert len(records(full, stream["name"])) > 0


class TestOdpRfcFailureSafety:
    """A failed delta run must not advance the position past unread rows."""

    @pytest.fixture(scope="class")
    def config(self, sap_rfc_config, odp_target):
        context, name = odp_target
        return {
            **sap_rfc_config,
            "protocol": {
                "mode": "odp_rfc",
                "context": context,
                "objects": [{"name": name, "context": context, "subscriber_process": "AB_E2E_FAILSAFE"}],
            },
        }

    @pytest.fixture
    def fresh(self, sap_rfc_config, odp_target, erpl_extensions):
        import duckdb

        context, name = odp_target
        con = duckdb.connect(config={"allow_unsigned_extensions": "true", "extension_directory": erpl_extensions})
        try:
            for ext in ("erpl_rfc", "erpl_odp"):
                con.load_extension(ext)
            con.execute("SET erpl_telemetry_enabled = false")
            con.execute(
                "CREATE OR REPLACE SECRET t (TYPE sap_rfc, ASHOST $h, SYSNR $n, CLIENT $c, "
                "USER $u, PASSWD $p, LANG $l)",
                {
                    "h": sap_rfc_config["ashost"],
                    "n": sap_rfc_config["sysnr"],
                    "c": sap_rfc_config["client"],
                    "u": sap_rfc_config["user"],
                    "p": sap_rfc_config["password"],
                    "l": sap_rfc_config["lang"],
                },
            )
            for pragma in (
                f"PRAGMA sap_odp_close_delta_cursor('{context}', 'AB_E2E_FAILSAFE', '{name}')",
                f"PRAGMA sap_odp_drop('{context}', 'ERPL', 'AB_E2E_FAILSAFE', '{name}')",
            ):
                try:
                    con.execute(pragma).fetchall()
                except Exception:
                    pass
        finally:
            con.close()
        yield

    def test_a_read_against_a_missing_object_emits_no_state(self, config, tmp_path, fresh, odp_target):
        """The stream fails, so no checkpoint may be written."""
        context, name = odp_target
        broken = {
            **config,
            "protocol": {
                **config["protocol"],
                "objects": [
                    {
                        "name": name,
                        "context": context,
                        "subscriber_process": "AB_E2E_FAILSAFE",
                        "columns": ["THIS_COLUMN_DOES_NOT_EXIST"],
                    }
                ],
            },
        }
        stream_name = f"{context}/{name}"
        stream = _discover(config, tmp_path, stream_name)
        messages = run_connector(
            "read",
            config=broken,
            catalog=_catalog(stream_name, stream["json_schema"], "incremental"),
            tmp_path=tmp_path,
        )
        assert errors(messages), "the read was supposed to fail"
        assert states(messages, stream_name) == [], (
            "a failed delta run must not checkpoint: the pointer would advance past rows that were never emitted"
        )
