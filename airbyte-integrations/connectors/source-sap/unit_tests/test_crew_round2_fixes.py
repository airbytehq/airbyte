"""Fixes for the second review round.

Each test names the failure mode rather than the code shape, because every one of
these was a silent-data-loss path rather than a crash.
"""

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository

from source_sap.cursors import FieldValueCursor
from source_sap.protocols.base import ReadPlan, SapObject
from source_sap.protocols.odp_rfc import OdpRfcDriver
from source_sap.protocols.rfc_invoke import RfcInvokeDriver, is_bapi_failure

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


def _plumbing():
    return InMemoryMessageRepository(), ConnectorStateManager()


def _record(data):
    record = MagicMock()
    record.data = data
    return record


def _states(repo):
    return [m.state.stream.stream_state.__dict__ for m in repo.consume_queue()]


class TestIncrementalDoesNotCheckpointMidStream:
    """F2: slicing made per-partition checkpointing unsafe.

    One slice finishing at a high value while a slice holding older rows is still
    running would checkpoint that high value; a crash then skips the older rows
    for good.
    """

    def _cursor(self):
        repo, mgr = _plumbing()
        return FieldValueCursor("S", None, repo, mgr, "C", {}), repo

    def test_closing_one_partition_emits_nothing(self):
        cursor, repo = self._cursor()
        cursor.observe(_record({"C": "2026-06-01"}))
        cursor.close_partition(MagicMock())
        assert _states(repo) == []

    def test_state_is_emitted_once_the_stream_completes(self):
        cursor, repo = self._cursor()
        cursor.observe(_record({"C": "2026-06-01"}))
        cursor.close_partition(MagicMock())
        cursor.ensure_at_least_one_state_emitted()
        assert _states(repo) == [{"C": "2026-06-01"}]

    def test_a_failed_stream_emits_no_state(self):
        cursor, repo = self._cursor()
        cursor.observe(_record({"C": "2026-06-01"}))
        cursor.mark_failed()
        cursor.ensure_at_least_one_state_emitted()
        assert _states(repo) == []


class TestOdpProbesOnceBeforeTheRead:
    """F3: re-probing after the read recorded changes that were never extracted."""

    def _driver(self):
        return OdpRfcDriver({**CONN, "protocol": {"mode": "odp_rfc", "context": "BW", "objects": [{"name": "N"}]}})

    def _obj(self):
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

    def test_the_state_records_the_timestamp_the_read_started_from(self):
        # SAP changes at T2 while the sync of T1's data is running. Recording T2
        # would mark those changes consumed without ever extracting them.
        session = self._session(20260101120000.0, 20260101130000.0)
        driver, obj = self._driver(), self._obj()
        driver.read_plans(session, obj, incremental=True, state={"subscriber_process": "AB_X", "initialized": True})
        state = driver.next_state(session, obj, {"subscriber_process": "AB_X"})
        assert state["last_modified"] == "20260101120000.0"

    def test_only_one_probe_is_issued_per_run(self):
        session = self._session(20260101120000.0, 20260101130000.0)
        driver, obj = self._driver(), self._obj()
        driver.read_plans(session, obj, incremental=True, state={"subscriber_process": "AB_X", "initialized": True})
        driver.next_state(session, obj, {"subscriber_process": "AB_X"})
        probes = [
            c for c in session.cursor.return_value.execute.call_args_list if "sap_odp_get_last_modified" in str(c)
        ]
        assert len(probes) == 1


class TestBapiReturnIsFoundWhateverItIsCalled:
    """F4: only a parameter literally named RETURN was inspected."""

    def _driver(self, **obj):
        return RfcInvokeDriver(
            {**CONN, "protocol": {"mode": "rfc_invoke", "objects": [{"name": "x", "function": "F", **obj}]}}
        )

    def _read(self, columns, values, **slice_):
        cursor = MagicMock()
        result = cursor.execute.return_value
        result.description = [(c, "x") for c in columns]
        result.fetchone.return_value = values
        plan = ReadPlan(sql="x", meta={"function": "F", "path_field": "T", **slice_})
        return list(self._driver().records_from(plan, cursor))

    @pytest.mark.parametrize("name", ["RETURN", "E_RETURN", "ET_RETURN", "T_RETURN", "RETURN_TAB", "EX_RETURN"])
    def test_an_error_is_caught_under_any_conventional_return_name(self, name):
        with pytest.raises(Exception, match="went wrong"):
            self._read(["T", name], ([{"A": 1}], [{"TYPE": "E", "MESSAGE": "went wrong"}]), return_field=name)

    def test_a_configured_return_parameter_wins(self):
        with pytest.raises(Exception, match="went wrong"):
            self._read(
                ["T", "ZZ_MESSAGES"], ([{"A": 1}], [{"TYPE": "E", "MESSAGE": "went wrong"}]), return_field="ZZ_MESSAGES"
            )

    def test_a_scalar_struct_return_does_not_crash(self):
        # F8: a RETURN surfaced as a single STRUCT made .get() run over dict keys.
        with pytest.raises(Exception, match="went wrong"):
            self._read(["T", "RETURN"], ([{"A": 1}], {"TYPE": "E", "MESSAGE": "went wrong"}), return_field="RETURN")

    def test_a_healthy_scalar_struct_return_is_not_a_failure(self):
        rows = self._read(["T", "RETURN"], ([{"A": 1}], {"TYPE": "S", "MESSAGE": "ok"}), return_field="RETURN")
        assert rows == [{"A": 1}]


class TestReturnShapeNormalisation:
    def test_a_mapping_is_treated_as_one_message(self):
        assert is_bapi_failure({"TYPE": "E", "MESSAGE": "x"})

    def test_a_healthy_mapping_is_not_a_failure(self):
        assert not is_bapi_failure({"TYPE": "S"})

    def test_a_list_of_strings_does_not_crash(self):
        assert not is_bapi_failure(["unexpected", "shape"])


class TestParameterNamesAreCanonicalised:
    """F6/F7: discovery accepted names that the read then failed on."""

    DESCRIBE = {
        "import": [{"name": "FLIGHTDATE", "duckdb_type": "DATE"}, {"name": "AIRLINE", "duckdb_type": "VARCHAR"}],
        "export": [],
        "changing": [],
        "tables": [{"name": "FLIGHT_LIST", "duckdb_type": "STRUCT(A VARCHAR)[]"}],
    }

    def _driver(self):
        return RfcInvokeDriver(
            {**CONN, "protocol": {"mode": "rfc_invoke", "objects": [{"name": "x", "function": "F"}]}}
        )

    def test_a_lower_case_parameter_is_canonicalised_to_the_sap_spelling(self):
        got = self._driver().canonical_parameters({"flightdate": "20260102"}, self.DESCRIBE)
        assert got == {"FLIGHTDATE": "20260102"}

    def test_a_canonicalised_parameter_is_then_cast_correctly(self):
        driver = self._driver()
        params = driver.canonical_parameters({"flightdate": "20260102"}, self.DESCRIBE)
        types = {"FLIGHTDATE": "DATE", "AIRLINE": "VARCHAR"}
        assert "DATE '2026-01-02'" in driver.render_parameters(params, types)

    def test_a_slice_parameter_is_validated(self):
        with pytest.raises(Exception, match="NOPE"):
            self._driver().validate_parameters("F", {"NOPE": None}, self.DESCRIBE)

    def test_a_cursor_parameter_typo_is_caught_at_discover(self):
        driver = self._driver()
        with pytest.raises(Exception, match="CURSOR_TYPO"):
            driver.validate_parameters("F", {"CURSOR_TYPO": None}, self.DESCRIBE)
