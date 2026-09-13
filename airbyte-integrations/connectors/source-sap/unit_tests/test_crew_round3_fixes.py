"""Fixes from crew round 3."""

from unittest.mock import MagicMock

import pytest

from source_sap.protocols.base import SapObject
from source_sap.protocols.rfc import RfcDriver

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


def _driver(**protocol):
    return RfcDriver({**CONN, "protocol": {"mode": "rfc", **protocol}})


def _obj(**meta):
    # No resume_key: resumable full refresh was withdrawn in round 3, because a
    # worker thread could emit its state ahead of the records it covered.
    return SapObject(
        name="T",
        json_schema={"type": "object", "properties": {}},
        primary_key=[["MANDT"], ["CARRID"]],
        meta={"table": "T", **meta},
    )


def _stream(driver, obj, incremental=False):
    from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
    from airbyte_cdk.sources.message import InMemoryMessageRepository

    from source_sap.cursors import NoStateCursor
    from source_sap.streams import build_stream

    cursor = NoStateCursor("T", None, InMemoryMessageRepository(), ConnectorStateManager())
    return build_stream(MagicMock(), driver, obj, cursor, incremental=incremental, state={})


class TestPartitionsAlwaysGovernTheSql:
    """One number must drive the SQL.

    With PARTITIONS omitted from the query, an absent setting meant one thing to
    the connector and another to what SAP actually did. It governed resumability
    too, until resumable full refresh was withdrawn in this same round.
    """

    def test_the_partition_count_is_always_stated(self):
        sql = _driver().read_plans(None, _obj(), incremental=False, state={})[0].sql
        assert "PARTITIONS := 0" in sql

    def test_a_configured_count_is_used(self):
        driver = _driver(objects=[{"name": "T", "partitions": 4}])
        sql = driver.read_plans(None, _obj(), incremental=False, state={})[0].sql
        assert "PARTITIONS := 4" in sql


class TestOdpProbeIsNotGatedByTheSkipSetting:
    """With skip_unchanged off, the probe used to happen after the read, which is
    the race the probe exists to avoid."""

    def _odp(self, **protocol):
        from source_sap.protocols.odp_rfc import OdpRfcDriver

        return OdpRfcDriver(
            {**CONN, "protocol": {"mode": "odp_rfc", "context": "BW", "objects": [{"name": "N"}], **protocol}}
        )

    def _odp_obj(self):
        return SapObject(
            name="BW/N",
            json_schema={},
            supports_incremental=True,
            meta={"context": "BW", "odp_name": "N", "subscriber_process": "AB_X"},
        )

    def _session(self, *timestamps):
        session = MagicMock()
        session.cursor.return_value.execute.return_value.fetchone.side_effect = [("N", t) for t in timestamps]
        return session

    def test_the_probe_runs_even_when_skipping_is_disabled(self):
        session = self._session(20260101120000.0, 20260101130000.0)
        driver, obj = self._odp(skip_unchanged=False), self._odp_obj()
        plans = driver.read_plans(
            session,
            obj,
            incremental=True,
            state={"subscriber_process": "AB_X", "initialized": True, "last_modified": "20260101120000.0"},
        )
        assert len(plans) == 1, "skipping is off, so it must read"
        state = driver.next_state(session, obj, {"subscriber_process": "AB_X"})
        # The value recorded is the one from before the read, not a later one.
        assert state["last_modified"] == "20260101120000.0"


class TestReturnGuardIsCaseInsensitive:
    """F6: SAP spells parameter names in upper case, but a Z-module or a
    lower-cased metadata source would slip past an exact-case match, and the
    guard fails open -- an unrecognised return table means a failed call reads
    as an empty stream."""

    def _read(self, columns, values, **slice_):
        from source_sap.protocols.base import ReadPlan
        from source_sap.protocols.rfc_invoke import RfcInvokeDriver

        cursor = MagicMock()
        result = cursor.execute.return_value
        result.description = [(c, "x") for c in columns]
        result.fetchone.return_value = values
        driver = RfcInvokeDriver(
            {**CONN, "protocol": {"mode": "rfc_invoke", "objects": [{"name": "x", "function": "F"}]}}
        )
        plan = ReadPlan(sql="x", meta={"function": "F", "path_field": "T", **slice_})
        return list(driver.records_from(plan, cursor))

    @pytest.mark.parametrize("name", ["return", "Return", "e_return", "Et_Return"])
    def test_a_lower_case_return_table_is_still_inspected(self, name):
        with pytest.raises(Exception, match="broke"):
            self._read(["T", name], ([{"A": 1}], [{"TYPE": "E", "MESSAGE": "broke"}]))

    def test_a_lower_case_type_field_is_still_read(self):
        from source_sap.protocols.rfc_invoke import is_bapi_failure

        assert is_bapi_failure([{"type": "E", "message": "broke"}])

    def test_a_lower_case_error_marker_is_caught(self):
        from source_sap.protocols.rfc_invoke import is_bapi_failure

        assert is_bapi_failure([{"TYPE": "e"}])
