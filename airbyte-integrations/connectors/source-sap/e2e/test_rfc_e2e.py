"""End-to-end RFC sync against a live SAP system. No mocks."""

from __future__ import annotations

import pytest

from e2e.conftest import errors, records, run_connector, states

pytestmark = pytest.mark.requires_creds


@pytest.fixture(scope="module")
def rfc_config(sap_rfc_config):
    return {**sap_rfc_config, "protocol": {"mode": "rfc", "table_pattern": "SFLIGHT"}}


def _catalog(stream: str, schema: dict, sync_mode: str = "full_refresh", cursor=None):
    configured = {
        "stream": {"name": stream, "json_schema": schema, "supported_sync_modes": ["full_refresh", "incremental"]},
        "sync_mode": sync_mode,
        "destination_sync_mode": "overwrite" if sync_mode == "full_refresh" else "append_dedup",
    }
    if cursor:
        configured["cursor_field"] = [cursor]
        configured["stream"]["default_cursor_field"] = [cursor]
    return {"streams": [configured]}


class TestCheck:
    def test_succeeds_against_the_real_system(self, rfc_config, tmp_path):
        messages = run_connector("check", config=rfc_config, tmp_path=tmp_path)
        status = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert status and status[0]["connectionStatus"]["status"] == "SUCCEEDED"

    def test_bad_password_fails_with_a_useful_message(self, rfc_config, tmp_path):
        messages = run_connector("check", config={**rfc_config, "password": "definitely-wrong"}, tmp_path=tmp_path)
        status = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert status and status[0]["connectionStatus"]["status"] == "FAILED"
        assert status[0]["connectionStatus"]["message"]

    def test_the_password_never_appears_in_the_output(self, rfc_config, tmp_path):
        messages = run_connector("check", config=rfc_config, tmp_path=tmp_path)
        blob = str(messages)
        assert rfc_config["password"] not in blob


class TestDiscover:
    def test_finds_the_table_with_a_real_schema(self, rfc_config, tmp_path):
        messages = run_connector("discover", config=rfc_config, tmp_path=tmp_path)
        catalogs = [m["catalog"] for m in messages if m.get("type") == "CATALOG"]
        assert catalogs
        streams = {s["name"]: s for s in catalogs[0]["streams"]}
        assert "SFLIGHT" in streams
        props = streams["SFLIGHT"]["json_schema"]["properties"]
        assert "CARRID" in props and "FLDATE" in props
        # SAP reports FLDATE as DATS and PRICE as CURR.
        assert props["FLDATE"] == {
            "type": ["null", "string"],
            "format": "date",
            "description": props["FLDATE"].get("description"),
        }
        assert props["PRICE"]["type"] == ["null", "number"]
        # MANDT/CARRID/CONNID/FLDATE are the SAP key of SFLIGHT.
        assert streams["SFLIGHT"]["source_defined_primary_key"] == [["MANDT"], ["CARRID"], ["CONNID"], ["FLDATE"]]


class TestRead:
    @pytest.fixture(scope="class")
    def schema(self, rfc_config, tmp_path_factory):
        messages = run_connector("discover", config=rfc_config, tmp_path=tmp_path_factory.mktemp("d"))
        catalog = [m["catalog"] for m in messages if m.get("type") == "CATALOG"][0]
        return next(s for s in catalog["streams"] if s["name"] == "SFLIGHT")["json_schema"]

    def test_emits_records_and_no_errors(self, rfc_config, schema, tmp_path):
        messages = run_connector("read", config=rfc_config, catalog=_catalog("SFLIGHT", schema), tmp_path=tmp_path)
        assert errors(messages) == []
        rows = records(messages, "SFLIGHT")
        assert len(rows) > 0
        assert {"MANDT", "CARRID", "FLDATE", "PRICE"} <= set(rows[0]["data"])

    def test_emitted_at_is_in_milliseconds(self, rfc_config, schema, tmp_path):
        # The previous connector used seconds, dating every record to 1970.
        messages = run_connector("read", config=rfc_config, catalog=_catalog("SFLIGHT", schema), tmp_path=tmp_path)
        emitted_at = records(messages, "SFLIGHT")[0]["emitted_at"]
        assert emitted_at > 1_600_000_000_000

    def test_decimal_and_date_values_survive_as_json(self, rfc_config, schema, tmp_path):
        messages = run_connector("read", config=rfc_config, catalog=_catalog("SFLIGHT", schema), tmp_path=tmp_path)
        row = records(messages, "SFLIGHT")[0]["data"]
        assert isinstance(row["FLDATE"], str) and row["FLDATE"].count("-") == 2
        assert isinstance(row["PRICE"], str)  # exact decimal, not a lossy float

    def test_a_state_message_is_emitted(self, rfc_config, schema, tmp_path):
        messages = run_connector("read", config=rfc_config, catalog=_catalog("SFLIGHT", schema), tmp_path=tmp_path)
        assert states(messages, "SFLIGHT")

    def test_column_projection_reaches_sap(self, rfc_config, schema, tmp_path):
        config = {
            **rfc_config,
            "protocol": {
                "mode": "rfc",
                "table_pattern": "SFLIGHT",
                "objects": [{"name": "SFLIGHT", "columns": ["CARRID", "CONNID", "FLDATE"]}],
            },
        }
        messages = run_connector("read", config=config, catalog=_catalog("SFLIGHT", schema), tmp_path=tmp_path)
        assert errors(messages) == []
        assert set(records(messages, "SFLIGHT")[0]["data"]) == {"CARRID", "CONNID", "FLDATE"}

    def test_sap_side_filter_reaches_sap(self, rfc_config, schema, tmp_path):
        config = {
            **rfc_config,
            "protocol": {
                "mode": "rfc",
                "table_pattern": "SFLIGHT",
                "objects": [{"name": "SFLIGHT", "filter": "CARRID = 'LH'"}],
            },
        }
        messages = run_connector("read", config=config, catalog=_catalog("SFLIGHT", schema), tmp_path=tmp_path)
        rows = records(messages, "SFLIGHT")
        assert rows and {r["data"]["CARRID"] for r in rows} == {"LH"}

    def test_partitioned_read_returns_the_same_rows(self, rfc_config, schema, tmp_path):
        base = run_connector(
            "read",
            config={**rfc_config, "protocol": {"mode": "rfc", "table_pattern": "SFLIGHT", "partitions": 0}},
            catalog=_catalog("SFLIGHT", schema),
            tmp_path=tmp_path,
        )
        parallel = run_connector(
            "read",
            config={**rfc_config, "protocol": {"mode": "rfc", "table_pattern": "SFLIGHT", "partitions": 8}},
            catalog=_catalog("SFLIGHT", schema),
            tmp_path=tmp_path,
        )
        assert errors(base) == [] and errors(parallel) == []

        # Partitioned scans return the same rows in an unspecified order.
        def key(rows):
            return sorted(tuple(sorted(r["data"].items())) for r in rows)

        left, right = key(records(base, "SFLIGHT")), key(records(parallel, "SFLIGHT"))
        # Guard first: two empty results compare equal, so without this the
        # assertion below holds just as well when both reads return nothing.
        assert len(left) > 0, "the serial read returned no SFLIGHT rows"
        assert left == right


class TestIncremental:
    @pytest.fixture(scope="class")
    def schema(self, rfc_config, tmp_path_factory):
        messages = run_connector("discover", config=rfc_config, tmp_path=tmp_path_factory.mktemp("d2"))
        catalog = [m["catalog"] for m in messages if m.get("type") == "CATALOG"][0]
        return next(s for s in catalog["streams"] if s["name"] == "SFLIGHT")["json_schema"]

    @pytest.fixture(scope="class")
    def incremental_config(self, rfc_config):
        return {
            **rfc_config,
            "protocol": {
                "mode": "rfc",
                "table_pattern": "SFLIGHT",
                "objects": [{"name": "SFLIGHT", "cursor_field": "FLDATE"}],
            },
        }

    def test_stream_advertises_incremental(self, incremental_config, tmp_path):
        messages = run_connector("discover", config=incremental_config, tmp_path=tmp_path)
        catalog = [m["catalog"] for m in messages if m.get("type") == "CATALOG"][0]
        stream = next(s for s in catalog["streams"] if s["name"] == "SFLIGHT")
        assert "incremental" in stream["supported_sync_modes"]

    def test_second_run_from_state_returns_fewer_rows(self, incremental_config, schema, tmp_path):
        first = run_connector(
            "read",
            config=incremental_config,
            catalog=_catalog("SFLIGHT", schema, "incremental", "FLDATE"),
            tmp_path=tmp_path,
        )
        assert errors(first) == []
        first_rows = records(first, "SFLIGHT")
        state = states(first, "SFLIGHT")[-1]
        assert state["stream"]["stream_state"].get("FLDATE")

        second = run_connector(
            "read",
            config=incremental_config,
            catalog=_catalog("SFLIGHT", schema, "incremental", "FLDATE"),
            state=[state],
            tmp_path=tmp_path,
        )
        assert errors(second) == []
        second_rows = records(second, "SFLIGHT")
        # Only the rows at or after the high-water mark come back.
        assert 0 < len(second_rows) < len(first_rows)
