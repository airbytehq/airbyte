"""State handling for the three incremental shapes."""

from unittest.mock import MagicMock

from airbyte_cdk.models import AirbyteStateType, Type
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository

from source_sap.cursors import DriverStateCursor, FieldValueCursor
from source_sap.protocols.base import SapObject


def _plumbing():
    return InMemoryMessageRepository(), ConnectorStateManager()


def _obj(**meta):
    return SapObject(name="S", json_schema={}, meta=meta)


class TestDriverStateCursor:
    def test_no_state_is_emitted_mid_stream(self):
        repo, mgr = _plumbing()
        driver = MagicMock()
        driver.next_state.return_value = {"subscriber_process": "AB_X"}
        cursor = DriverStateCursor("S", None, repo, mgr, driver, MagicMock(), _obj(), {})
        cursor.close_partition(MagicMock())
        # A server-side pointer must not be checkpointed until the whole run is
        # consumed, or the next sync skips un-acked packets.
        assert list(repo.consume_queue()) == []

    def test_state_is_emitted_once_at_the_end(self):
        repo, mgr = _plumbing()
        driver = MagicMock()
        driver.next_state.return_value = {"subscriber_process": "AB_X", "initialized": True}
        cursor = DriverStateCursor("S", None, repo, mgr, driver, MagicMock(), _obj(), {})
        cursor.close_partition(MagicMock())
        cursor.ensure_at_least_one_state_emitted()
        messages = list(repo.consume_queue())
        assert len(messages) == 1
        assert messages[0].type == Type.STATE
        assert messages[0].state.type == AirbyteStateType.STREAM
        assert messages[0].state.stream.stream_state.subscriber_process == "AB_X"

    def test_driver_cleanup_runs_before_the_checkpoint(self):
        repo, mgr = _plumbing()
        driver, session = MagicMock(), MagicMock()
        driver.next_state.return_value = {"subscriber_process": "AB_X"}
        cursor = DriverStateCursor("S", None, repo, mgr, driver, session, _obj(), {})
        cursor.ensure_at_least_one_state_emitted()
        driver.on_success.assert_called_once()

    def test_a_failed_partition_suppresses_the_checkpoint(self):
        repo, mgr = _plumbing()
        driver = MagicMock()
        cursor = DriverStateCursor("S", None, repo, mgr, driver, MagicMock(), _obj(), {})
        cursor.mark_failed()
        cursor.ensure_at_least_one_state_emitted()
        assert list(repo.consume_queue()) == []
        driver.on_success.assert_not_called()


class TestFieldValueCursor:
    def _cursor(self, initial=None):
        repo, mgr = _plumbing()
        return FieldValueCursor("S", None, repo, mgr, "FLDATE", initial or {}), repo

    def test_tracks_the_maximum_observed_value(self):
        cursor, _ = self._cursor()
        for value in ["20260101", "20260305", "20260202"]:
            cursor.observe(_record({"FLDATE": value}))
        assert cursor.state["FLDATE"] == "20260305"

    def test_never_moves_backwards_from_prior_state(self):
        cursor, _ = self._cursor({"FLDATE": "20260601"})
        cursor.observe(_record({"FLDATE": "20260101"}))
        assert cursor.state["FLDATE"] == "20260601"

    def test_nulls_are_ignored(self):
        cursor, _ = self._cursor({"FLDATE": "20260101"})
        cursor.observe(_record({"FLDATE": None}))
        assert cursor.state["FLDATE"] == "20260101"

    def test_closing_a_partition_emits_nothing(self):
        """A stream can be split across several plans (slice_by), read in
        parallel, so checkpointing a partial maximum would let the next run's
        `>=` predicate skip a slower slice's rows."""
        cursor, repo = self._cursor()
        cursor.observe(_record({"FLDATE": "20260101"}))
        cursor.close_partition(MagicMock())
        assert list(repo.consume_queue()) == []

    def test_state_is_emitted_when_the_stream_completes(self):
        cursor, repo = self._cursor()
        cursor.observe(_record({"FLDATE": "20260101"}))
        cursor.close_partition(MagicMock())
        cursor.ensure_at_least_one_state_emitted()
        assert len(list(repo.consume_queue())) == 1


def _record(data):
    rec = MagicMock()
    rec.data = data
    return rec


class TestFieldValueCursorOrdering:
    """A high-water mark compares values; the comparison has to be right."""

    def _cursor(self, initial=None):
        repo, mgr = _plumbing()
        return FieldValueCursor("S", None, repo, mgr, "C", initial or {}), repo

    def test_numeric_values_compare_numerically(self):
        # Lexicographic comparison would keep "9" over "10".
        cursor, _ = self._cursor()
        for value in [9, 10, 3]:
            cursor.observe(_record({"C": value}))
        assert cursor.state["C"] == 10

    def test_numeric_strings_compare_numerically(self):
        cursor, _ = self._cursor()
        for value in ["9", "10"]:
            cursor.observe(_record({"C": value}))
        assert cursor.state["C"] == "10"

    def test_dates_still_compare_correctly(self):
        cursor, _ = self._cursor()
        for value in ["2026-01-02", "2026-01-10", "2026-01-05"]:
            cursor.observe(_record({"C": value}))
        assert cursor.state["C"] == "2026-01-10"

    def test_sap_dats_values_compare_correctly(self):
        cursor, _ = self._cursor()
        for value in ["20260102", "20260110"]:
            cursor.observe(_record({"C": value}))
        assert cursor.state["C"] == "20260110"

    def test_mixed_types_do_not_crash(self):
        cursor, _ = self._cursor()
        cursor.observe(_record({"C": 5}))
        cursor.observe(_record({"C": "abc"}))
        assert cursor.state["C"] is not None
