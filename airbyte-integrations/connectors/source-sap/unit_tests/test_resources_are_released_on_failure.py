"""A failed sync must still hand back what it took from SAP.

Suppressing the checkpoint is right -- the next run has to resume from the same
position -- but it was also suppressing the *cleanup*, because both hung off
`on_success`. An ODP delta read that fails therefore left its delta cursor
reserved on the SAP side until it timed out, and the next run met
ILLEGAL_REQ_STATE_FOR_CONFIRM.

Releasing is safe on the failure path: erpl's close calls RODPS_REPL_ODP_CLOSE,
which does not confirm the packets -- a cursor left mid-fetch is refused, and
the refusal is reported, which is strictly more than the silence it replaces.
"""

from unittest.mock import MagicMock

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository

from source_sap.cursors import DriverStateCursor
from source_sap.protocols.base import SapObject


def _cursor(driver):
    return DriverStateCursor(
        "S",
        None,
        InMemoryMessageRepository(),
        ConnectorStateManager(),
        driver,
        MagicMock(),
        SapObject(name="S", json_schema={}),
        {"subscriber_process": "p"},
    )


class TestAFailedStream:
    def test_releases_the_sap_side_resource(self):
        driver = MagicMock()
        cursor = _cursor(driver)
        cursor.mark_failed()
        cursor.ensure_at_least_one_state_emitted()
        assert driver.release.called, "a failed stream left the ODP delta cursor open"

    def test_still_does_not_checkpoint(self):
        driver = MagicMock()
        cursor = _cursor(driver)
        cursor.mark_failed()
        cursor.ensure_at_least_one_state_emitted()
        assert not driver.next_state.called
        assert not driver.on_success.called

    def test_a_failing_release_does_not_raise(self):
        # Cleanup runs on the way out of a run that is already failing.
        driver = MagicMock()
        driver.release.side_effect = RuntimeError("the connection is gone")
        cursor = _cursor(driver)
        cursor.mark_failed()
        cursor.ensure_at_least_one_state_emitted()

    def test_releases_once_however_often_it_is_asked(self):
        driver = MagicMock()
        cursor = _cursor(driver)
        cursor.mark_failed()
        cursor.ensure_at_least_one_state_emitted()
        cursor.ensure_at_least_one_state_emitted()
        assert driver.release.call_count == 1


class TestASuccessfulStream:
    def test_releases_and_checkpoints(self):
        driver = MagicMock()
        driver.next_state.return_value = {"subscriber_process": "p"}
        cursor = _cursor(driver)
        cursor.ensure_at_least_one_state_emitted()
        assert driver.release.called and driver.next_state.called

    def test_releases_once(self):
        driver = MagicMock()
        driver.next_state.return_value = {}
        cursor = _cursor(driver)
        cursor.ensure_at_least_one_state_emitted()
        cursor.ensure_at_least_one_state_emitted()
        assert driver.release.call_count == 1
