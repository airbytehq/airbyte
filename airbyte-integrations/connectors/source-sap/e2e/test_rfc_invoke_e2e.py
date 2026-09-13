"""Calling real SAP function modules end to end. Nothing mocked."""

from __future__ import annotations

import pytest

from e2e.conftest import errors, records, run_connector, states

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


def _discover(config, tmp_path, name):
    messages = run_connector("discover", config=config, tmp_path=tmp_path)
    catalogs = [m["catalog"] for m in messages if m.get("type") == "CATALOG"]
    assert catalogs, f"discover produced no catalog: {messages[-2:]}"
    return next(s for s in catalogs[0]["streams"] if s["name"] == name)


@pytest.fixture(scope="module")
def flights_config(sap_rfc_config):
    return {
        **sap_rfc_config,
        "protocol": {
            "mode": "rfc_invoke",
            "objects": [
                {
                    "name": "flights",
                    "function": "BAPI_FLIGHT_GETLIST",
                    "path": "/FLIGHT_LIST",
                    "parameters": {"AIRLINE": "LH"},
                    "primary_key": ["AIRLINEID", "CONNECTID", "FLIGHTDATE"],
                }
            ],
        },
    }


class TestCheck:
    def test_check_resolves_the_function_module(self, flights_config, tmp_path):
        messages = run_connector("check", config=flights_config, tmp_path=tmp_path)
        status = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert status and status[0]["connectionStatus"]["status"] == "SUCCEEDED"

    def test_an_unknown_function_module_fails_the_check(self, sap_rfc_config, tmp_path):
        config = {
            **sap_rfc_config,
            "protocol": {"mode": "rfc_invoke", "objects": [{"name": "x", "function": "Z_DEFINITELY_NOT_A_FUNCTION"}]},
        }
        messages = run_connector("check", config=config, tmp_path=tmp_path)
        status = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert status and status[0]["connectionStatus"]["status"] == "FAILED"
        assert "Z_DEFINITELY_NOT_A_FUNCTION" in status[0]["connectionStatus"]["message"]


class TestDiscoverDoesNotInvoke:
    def test_the_schema_comes_from_metadata_with_the_right_types(self, flights_config, tmp_path):
        stream = _discover(flights_config, tmp_path, "flights")
        props = stream["json_schema"]["properties"]
        assert {"AIRLINEID", "CONNECTID", "FLIGHTDATE", "PRICE"} <= set(props)
        assert props["FLIGHTDATE"]["format"] == "date"
        assert props["DEPTIME"]["format"] == "time"
        assert props["PRICE"]["type"] == ["null", "number"]
        assert stream["source_defined_primary_key"] == [["AIRLINEID"], ["CONNECTID"], ["FLIGHTDATE"]]

    def test_discover_makes_no_call_to_the_function_module(self, sap_rfc_config, tmp_path):
        """The whole safety argument: discovering must not have side effects.

        `BAPI_FLIGHT_SAVEREPLICA` writes. Discovery has to describe it without
        calling it, which is why the schema is derived from the interface
        metadata rather than from a probe call.
        """
        config = {
            **sap_rfc_config,
            "protocol": {
                "mode": "rfc_invoke",
                "objects": [
                    {
                        "name": "writer",
                        "function": "BAPI_FLIGHT_SAVEREPLICA",
                        "path": "/RETURN",
                    }
                ],
            },
        }
        messages = run_connector("discover", config=config, tmp_path=tmp_path)
        catalogs = [m["catalog"] for m in messages if m.get("type") == "CATALOG"]
        assert catalogs, "a write-capable module must still be describable"
        assert catalogs[0]["streams"][0]["json_schema"]["properties"]
        # Nothing in the log may claim an invocation happened.
        assert not any("sap_rfc_invoke" in str(m.get("log", {}).get("message", "")) for m in messages)


class TestRead:
    def test_the_result_table_becomes_the_records(self, flights_config, tmp_path):
        stream = _discover(flights_config, tmp_path, "flights")
        messages = run_connector(
            "read", config=flights_config, catalog=_catalog("flights", stream["json_schema"]), tmp_path=tmp_path
        )
        assert errors(messages) == []
        rows = records(messages, "flights")
        assert len(rows) > 0
        assert {r["data"]["AIRLINEID"] for r in rows} == {"LH"}

    def test_typed_values_survive_as_json(self, flights_config, tmp_path):
        stream = _discover(flights_config, tmp_path, "flights")
        messages = run_connector(
            "read", config=flights_config, catalog=_catalog("flights", stream["json_schema"]), tmp_path=tmp_path
        )
        row = records(messages, "flights")[0]["data"]
        assert row["FLIGHTDATE"].count("-") == 2
        assert ":" in row["DEPTIME"]
        assert isinstance(row["PRICE"], str)  # exact decimal, not a lossy float

    def test_a_state_message_is_emitted(self, flights_config, tmp_path):
        stream = _discover(flights_config, tmp_path, "flights")
        messages = run_connector(
            "read", config=flights_config, catalog=_catalog("flights", stream["json_schema"]), tmp_path=tmp_path
        )
        assert states(messages, "flights")

    def test_without_a_path_the_scalar_exports_are_one_record(self, sap_rfc_config, tmp_path):
        config = {
            **sap_rfc_config,
            "protocol": {
                "mode": "rfc_invoke",
                "objects": [
                    {
                        "name": "ping",
                        "function": "STFC_CONNECTION",
                        "parameters": {"REQUTEXT": "hello from airbyte"},
                    }
                ],
            },
        }
        stream = _discover(config, tmp_path, "ping")
        assert set(stream["json_schema"]["properties"]) == {"ECHOTEXT", "RESPTEXT"}
        messages = run_connector(
            "read", config=config, catalog=_catalog("ping", stream["json_schema"]), tmp_path=tmp_path
        )
        assert errors(messages) == []
        rows = records(messages, "ping")
        assert len(rows) == 1
        assert rows[0]["data"]["ECHOTEXT"] == "hello from airbyte"


class TestSlicing:
    def test_one_call_per_slice_and_the_union_of_their_rows(self, sap_rfc_config, tmp_path):
        config = {
            **sap_rfc_config,
            "protocol": {
                "mode": "rfc_invoke",
                "objects": [
                    {
                        "name": "flights",
                        "function": "BAPI_FLIGHT_GETLIST",
                        "path": "/FLIGHT_LIST",
                        "slice_by": {"parameter": "AIRLINE", "values": ["LH", "AA", "UA"]},
                    }
                ],
            },
        }
        stream = _discover(config, tmp_path, "flights")
        messages = run_connector(
            "read", config=config, catalog=_catalog("flights", stream["json_schema"]), tmp_path=tmp_path
        )
        assert errors(messages) == []
        airlines = {r["data"]["AIRLINEID"] for r in records(messages, "flights")}
        assert airlines == {"LH", "AA", "UA"}


class TestErrorsAreNotSilent:
    def test_a_bad_parameter_fails_with_our_message(self, sap_rfc_config, tmp_path):
        config = {
            **sap_rfc_config,
            "protocol": {
                "mode": "rfc_invoke",
                "objects": [
                    {
                        "name": "flights",
                        "function": "BAPI_FLIGHT_GETLIST",
                        "path": "/FLIGHT_LIST",
                        "parameters": {"NOT_A_PARAMETER": "x"},
                    }
                ],
            },
        }
        messages = run_connector("discover", config=config, tmp_path=tmp_path)
        traces = errors(messages)
        assert traces, "an unknown parameter must fail rather than be ignored"
        # Our message names the offender and lists the alternatives.
        assert "NOT_A_PARAMETER" in traces[0]["error"]["message"]
        assert "AIRLINE" in traces[0]["error"]["message"]

    def test_a_bad_path_fails_with_our_message(self, sap_rfc_config, tmp_path):
        config = {
            **sap_rfc_config,
            "protocol": {
                "mode": "rfc_invoke",
                "objects": [
                    {
                        "name": "flights",
                        "function": "BAPI_FLIGHT_GETLIST",
                        "path": "/NOPE",
                    }
                ],
            },
        }
        traces = errors(run_connector("discover", config=config, tmp_path=tmp_path))
        assert traces and "FLIGHT_LIST" in traces[0]["error"]["message"]

    def test_a_bapi_error_return_fails_the_stream(self, sap_rfc_config, tmp_path):
        """A BAPI answers RFC_OK and reports failure in RETURN.

        Without the RETURN check this is indistinguishable from an empty result,
        and the sync would report success having synced nothing.
        """
        config = {
            **sap_rfc_config,
            "protocol": {
                "mode": "rfc_invoke",
                "objects": [
                    {
                        "name": "detail",
                        "function": "BAPI_FLIGHT_GETDETAIL",
                        "path": "/RETURN",
                        "parameters": {"AIRLINEID": "ZZ", "CONNECTIONID": "9999", "FLIGHTDATE": "20260101"},
                    }
                ],
            },
        }
        stream = _discover(config, tmp_path, "detail")
        messages = run_connector(
            "read", config=config, catalog=_catalog("detail", stream["json_schema"]), tmp_path=tmp_path
        )
        traces = errors(messages)
        assert traces, "a BAPI error must fail the stream, not produce an empty one"
        assert "BAPI_FLIGHT_GETDETAIL" in traces[0]["error"]["message"]
