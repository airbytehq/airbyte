"""End-to-end BICS sync against a live SAP BW system."""

from __future__ import annotations

import pytest

from e2e.conftest import errors, records, run_connector

pytestmark = pytest.mark.requires_creds


def _catalog(stream: str, schema: dict):
    return {
        "streams": [
            {
                "stream": {"name": stream, "json_schema": schema, "supported_sync_modes": ["full_refresh"]},
                "sync_mode": "full_refresh",
                "destination_sync_mode": "overwrite",
            }
        ]
    }


@pytest.fixture(scope="module")
def config(sap_rfc_config, bics_cube):
    return {
        **sap_rfc_config,
        "protocol": {
            "mode": "bics",
            "objects": [{"name": "cube", "cube": bics_cube}],
        },
    }


def test_check_sees_the_bw_infoproviders(config, tmp_path):
    messages = run_connector("check", config=config, tmp_path=tmp_path)
    status = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
    assert status and status[0]["connectionStatus"]["status"] == "SUCCEEDED"


def test_discover_returns_the_query_result_columns(config, tmp_path):
    messages = run_connector("discover", config=config, tmp_path=tmp_path)
    catalog = [m["catalog"] for m in messages if m.get("type") == "CATALOG"]
    assert catalog, f"discover produced no catalog: {messages[-2:]}"
    stream = catalog[0]["streams"][0]
    assert stream["json_schema"]["properties"]
    # BICS offers no change tracking.
    assert stream["supported_sync_modes"] == ["full_refresh"]


def test_read_returns_rows_without_the_grand_total(config, tmp_path, bics_cube):
    discover = run_connector("discover", config=config, tmp_path=tmp_path)
    stream = [m["catalog"] for m in discover if m.get("type") == "CATALOG"][0]["streams"][0]

    # Naming a row characteristic is what lets the connector recognise and drop
    # the "Overall Result" row BW appends to every result set.
    row_axis = next(iter(stream["json_schema"]["properties"]))
    sliced = {
        **config,
        "protocol": {
            "mode": "bics",
            "objects": [
                {"name": "cube", "cube": bics_cube, "rows": [row_axis]},
            ],
        },
    }
    messages = run_connector("read", config=sliced, catalog=_catalog("cube", stream["json_schema"]), tmp_path=tmp_path)
    assert errors(messages) == []
    rows = records(messages, "cube")
    assert rows
    totals = {"SUMME", "OVERALL RESULT", "GESAMTERGEBNIS", "RESULT"}
    assert not any(str(r["data"].get(row_axis, "")).upper() in totals for r in rows)
