"""Skipping an ODP delta read when SAP says nothing changed.

`sap_odp_get_last_modified` costs one RFC call and no rows. Opening a delta
cursor to discover there are no changes costs a subscription round trip and
leaves a cursor to close, so probing first is worth it on a stream that is
usually quiet.
"""

from unittest.mock import MagicMock

from source_sap.protocols.base import SapObject
from source_sap.protocols.odp_rfc import OdpRfcDriver

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


def driver(**protocol):
    return OdpRfcDriver({**CONN, "protocol": {"mode": "odp_rfc", "context": "BW", **protocol}})


def obj():
    return SapObject(
        name="BW/N",
        json_schema={},
        supports_incremental=True,
        meta={"context": "BW", "odp_name": "N", "subscriber_process": "AB_X"},
    )


def session_reporting(last_modified):
    session = MagicMock()
    session.cursor.return_value.execute.return_value.fetchone.return_value = (
        ("N", last_modified) if last_modified is not None else None
    )
    return session


class TestProbe:
    def test_the_probe_reads_the_last_modified_timestamp(self):
        session = session_reporting(20260101120000.0)
        assert driver().last_modified(session, "BW", "N") == "20260101120000.0"
        sql = session.cursor.return_value.execute.call_args[0][0]
        assert "sap_odp_get_last_modified('BW', 'N')" in sql

    def test_a_missing_row_reads_as_unknown(self):
        assert driver().last_modified(session_reporting(None), "BW", "N") is None

    def test_a_probe_failure_reads_as_unknown_rather_than_failing(self):
        # The probe is an optimisation; losing it must not fail the sync.
        session = MagicMock()
        session.cursor.return_value.execute.side_effect = RuntimeError("no auth")
        assert driver().last_modified(session, "BW", "N") is None


class TestSkipDecision:
    def test_an_unchanged_timestamp_produces_no_read_plans(self):
        session = session_reporting(20260101120000.0)
        plans = driver().read_plans(
            session,
            obj(),
            incremental=True,
            state={"subscriber_process": "AB_X", "initialized": True, "last_modified": "20260101120000.0"},
        )
        assert plans == []

    def test_an_advanced_timestamp_produces_a_delta_read(self):
        session = session_reporting(20260102120000.0)
        plans = driver().read_plans(
            session,
            obj(),
            incremental=True,
            state={"subscriber_process": "AB_X", "initialized": True, "last_modified": "20260101120000.0"},
        )
        assert len(plans) == 1 and "sap_odp_read_delta" in plans[0].sql

    def test_the_first_run_always_reads(self):
        # No stored timestamp means no DELTAINIT has happened yet.
        session = session_reporting(20260101120000.0)
        plans = driver().read_plans(session, obj(), incremental=True, state={})
        assert len(plans) == 1

    def test_an_unknown_timestamp_falls_back_to_reading(self):
        session = session_reporting(None)
        plans = driver().read_plans(
            session,
            obj(),
            incremental=True,
            state={"initialized": True, "last_modified": "20260101120000.0"},
        )
        assert len(plans) == 1

    def test_full_refresh_never_skips(self):
        session = session_reporting(20260101120000.0)
        plans = driver().read_plans(
            session,
            obj(),
            incremental=False,
            state={"last_modified": "20260101120000.0"},
        )
        assert len(plans) == 1 and "sap_odp_read_full" in plans[0].sql

    def test_the_probe_can_be_switched_off(self):
        session = session_reporting(20260101120000.0)
        plans = driver(skip_unchanged=False).read_plans(
            session,
            obj(),
            incremental=True,
            state={"initialized": True, "last_modified": "20260101120000.0"},
        )
        assert len(plans) == 1


class TestStateCarriesTheTimestamp:
    def test_next_state_records_the_probed_timestamp(self):
        session = session_reporting(20260102120000.0)
        state = driver().next_state(session, obj(), {"subscriber_process": "AB_X"})
        assert state["last_modified"] == "20260102120000.0"

    def test_an_unknown_timestamp_leaves_the_previous_one_alone(self):
        session = session_reporting(None)
        state = driver().next_state(session, obj(), {"subscriber_process": "AB_X", "last_modified": "20260101120000.0"})
        assert state["last_modified"] == "20260101120000.0"


class TestSkippedStreamStillCheckpoints:
    def test_a_skipped_stream_keeps_its_position(self):
        # Emitting no state would look like a reset on the next run.
        session = session_reporting(20260101120000.0)
        d = driver()
        state = {"subscriber_process": "AB_X", "initialized": True, "last_modified": "20260101120000.0"}
        assert d.read_plans(session, obj(), incremental=True, state=state) == []
        assert d.next_state(session, obj(), state)["subscriber_process"] == "AB_X"

    def test_a_skipped_stream_does_not_try_to_close_a_cursor(self):
        session = session_reporting(20260101120000.0)
        d = driver()
        state = {"subscriber_process": "AB_X", "initialized": True, "last_modified": "20260101120000.0"}
        d.read_plans(session, obj(), incremental=True, state=state)
        session.cursor.return_value.execute.reset_mock()
        d.release(session, obj(), state)
        executed = " ".join(str(c) for c in session.cursor.return_value.execute.call_args_list)
        assert "close_delta_cursor" not in executed
