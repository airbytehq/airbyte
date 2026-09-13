"""Concurrent-CDK cursors for the two incremental shapes SAP offers.

* :class:`FieldValueCursor` -- an ordinary high-water mark on a record field,
  used by the RFC protocol where the user nominates a date/timestamp column.
* :class:`DriverStateCursor` -- a *server-side* position (an ODP subscription or
  a delta token). Its defining rule: the position may only be checkpointed once
  the entire run has been consumed. A mid-run checkpoint would let the next sync
  resume past packets that were fetched but never emitted.
"""

from __future__ import annotations

import decimal
import logging
import threading
from collections.abc import Mapping
from typing import Any

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.types import Record, StreamSlice

logger = logging.getLogger("airbyte")


class _BaseCursor(Cursor):
    def __init__(
        self,
        stream_name: str,
        namespace: str | None,
        message_repository: MessageRepository,
        state_manager: ConnectorStateManager,
    ) -> None:
        self._stream_name = stream_name
        self._namespace = namespace
        self._message_repository = message_repository
        self._state_manager = state_manager
        self._lock = threading.Lock()

    @property
    def cursor_field(self) -> Any:  # the CDK only reads this for slice generation
        return None

    def stream_slices(self):
        yield StreamSlice(partition={}, cursor_slice={})

    def should_be_synced(self, record: Record) -> bool:
        return True

    @staticmethod
    def _sort_key(value: Any) -> tuple[int, decimal.Decimal, str]:
        """Order numerics numerically and everything else lexicographically.

        A plain string comparison keeps "9" over "10", which silently skips every
        key from 10 up. Dates and SAP DATS values sort correctly either way, so
        only the numeric case needs handling.

        `Decimal`, not `float`: SAP NUMC and DEC values are decimal strings that
        outrun a double's 53-bit mantissa, and two adjacent values would then
        share a key -- a cursor that never advances past the boundary and a sync
        that re-reads the same rows every run, silently.
        """
        try:
            number = decimal.Decimal(str(value))
        except (TypeError, ValueError, ArithmeticError):
            return (1, decimal.Decimal(0), str(value))
        if not number.is_finite():
            # "NaN" and "Infinity" parse as Decimals and then compare by rules
            # nobody wants in a high-water mark; as text they are just text.
            return (1, decimal.Decimal(0), str(value))
        return (0, number, "")

    def mark_failed(self) -> None:
        """Called when the stream did not finish. Cursors that persist a
        position override this to suppress their checkpoint."""

    def _emit(self, state: Mapping[str, Any]) -> None:
        self._state_manager.update_state_for_stream(self._stream_name, self._namespace, dict(state))
        self._message_repository.emit_message(
            self._state_manager.create_state_message(self._stream_name, self._namespace)
        )


class FieldValueCursor(_BaseCursor):
    """High-water mark over one record field."""

    def __init__(
        self,
        stream_name: str,
        namespace: str | None,
        message_repository: MessageRepository,
        state_manager: ConnectorStateManager,
        cursor_field: str,
        initial_state: Mapping[str, Any],
    ) -> None:
        super().__init__(stream_name, namespace, message_repository, state_manager)
        self._field = cursor_field
        self._value: Any = (initial_state or {}).get(cursor_field)
        self._failed = False

    @property
    def state(self) -> dict[str, Any]:
        return {self._field: self._value} if self._value is not None else {}

    def observe(self, record: Record) -> None:
        value = (record.data or {}).get(self._field)
        if value is None:
            return
        with self._lock:
            # Partitions are read out of order, so take the maximum rather than
            # the last value seen.
            if self._value is None or self._sort_key(value) > self._sort_key(self._value):
                self._value = value

    def close_partition(self, partition: Partition) -> None:
        """Deliberately no checkpoint.

        A stream can now be split across several plans -- `slice_by` on the
        function-invoke and BICS drivers does exactly that -- and the slices are
        read in parallel. Checkpointing the maximum seen so far while a slice
        holding older rows is still running would let the next run's `>=`
        predicate skip that slice's rows for good.
        """
        return

    def mark_failed(self) -> None:
        """Suppress the checkpoint so a failed run is retried from where it was."""
        with self._lock:
            self._failed = True

    def ensure_at_least_one_state_emitted(self) -> None:
        with self._lock:
            if self._failed:
                logger.warning(
                    "Not checkpointing %s: the stream did not complete, so the next sync "
                    "resumes from the previous cursor value.",
                    self._stream_name,
                )
                return
        self._emit(self.state)


class DriverStateCursor(_BaseCursor):
    """A position owned by SAP, checkpointed exactly once at the end of the run."""

    def __init__(
        self,
        stream_name: str,
        namespace: str | None,
        message_repository: MessageRepository,
        state_manager: ConnectorStateManager,
        driver: Any,
        session: Any,
        sap_object: Any,
        initial_state: Mapping[str, Any],
    ) -> None:
        super().__init__(stream_name, namespace, message_repository, state_manager)
        self._driver = driver
        self._session = session
        self._object = sap_object
        self._state: dict[str, Any] = dict(initial_state or {})
        self._failed = False
        self._emitted = False
        self._released = False

    @property
    def state(self) -> dict[str, Any]:
        return dict(self._state)

    def observe(self, record: Record) -> None:
        """Runs on worker threads; the position comes from SAP, not the records."""

    def mark_failed(self) -> None:
        """Suppress the checkpoint so a failed run is retried from the same position."""
        with self._lock:
            self._failed = True

    def close_partition(self, partition: Partition) -> None:
        # Deliberately no checkpoint here. See the module docstring.
        return

    def _release(self) -> None:
        """Hand the SAP-side resource back, whether or not the stream completed."""
        with self._lock:
            if self._released:
                return
            self._released = True
        if self._failed:
            # Stated at INFO because it is the one cleanup a failed run still
            # performs, and an operator reading the log after a failure is
            # entitled to know the SAP side was handed back.
            logger.info("Releasing SAP-side resources for %s after a failed read.", self._stream_name)
        try:
            self._driver.release(self._session, self._object, self._state)
        except Exception:  # on the way out of a run that may already be failing
            logger.warning("Releasing SAP resources for %s failed.", self._stream_name, exc_info=True)

    def ensure_at_least_one_state_emitted(self) -> None:
        with self._lock:
            failed, done = self._failed, self._emitted
            if not (failed or done):
                self._emitted = True
        # Before the early return: a failed stream owes SAP its cursor back even
        # though it owes the platform no checkpoint.
        self._release()
        if failed or done:
            if failed:
                logger.warning(
                    "Not checkpointing %s: the stream did not complete, so the next sync "
                    "resumes from the previous position.",
                    self._stream_name,
                )
            return
        try:
            self._driver.on_success(self._session, self._object, self._state)
        except Exception:  # cleanup must never lose the checkpoint
            logger.warning("Post-read cleanup for %s failed.", self._stream_name, exc_info=True)
        self._state = dict(self._driver.next_state(self._session, self._object, self._state))
        self._emit(self._state)


class NoStateCursor(_BaseCursor):
    """Full-refresh streams still owe the platform one state message."""

    @property
    def state(self) -> dict[str, Any]:
        return {}

    def observe(self, record: Record) -> None:
        return

    def close_partition(self, partition: Partition) -> None:
        return

    def ensure_at_least_one_state_emitted(self) -> None:
        self._emit({"__ab_full_refresh_state_message": True})
