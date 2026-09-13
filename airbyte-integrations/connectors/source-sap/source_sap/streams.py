"""Concurrent-CDK streams over ERPL read plans."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.types import Record

from source_sap.errors import traced
from source_sap.protocols.base import ProtocolDriver, ReadPlan, SapObject
from source_sap.session import ErplSession

logger = logging.getLogger("airbyte")

# How often a long-running scan reports progress, so the platform's
# maxSecondsBetweenMessages budget is not hit during a slow SAP fetch.
_HEARTBEAT_SECONDS = 60


CDC_DELETED_AT = "_ab_cdc_deleted_at"


def declare_cdc_column(json_schema: Mapping[str, Any], sap_object: SapObject) -> dict[str, Any]:
    """Add the CDC tombstone to a delta-capable stream's schema.

    Records carry it, so the schema has to as well: a typed destination is
    entitled to drop a field the schema does not declare, and the tombstone is
    the whole reason to choose ODP over a snapshot.
    """
    schema = dict(json_schema)
    if not sap_object.change_mode_field:
        return schema
    properties = dict(schema.get("properties") or {})
    properties[CDC_DELETED_AT] = {
        "type": ["null", "string"],
        "format": "date-time",
        "description": "Set when SAP reported this row as deleted.",
    }
    schema["properties"] = properties
    return schema


class ErplPartition(Partition):
    """One read plan, executed on a thread-local DuckDB cursor."""

    def __init__(
        self,
        stream_name: str,
        session: ErplSession,
        plan: ReadPlan,
        change_mode_field: str | None,
        driver: Any,
        row_filter: Any | None = None,
        cursor: Any | None = None,
    ) -> None:
        self._stream_name = stream_name
        self._session = session
        self._plan = plan
        self._change_mode_field = change_mode_field
        self._row_filter = row_filter
        self._cursor = cursor
        self._driver = driver

    def stream_name(self) -> str:
        return self._stream_name

    def to_slice(self) -> Mapping[str, Any] | None:
        return dict(self._plan.slice_)

    def __hash__(self) -> int:
        return hash((self._stream_name, self._plan.sql, tuple(map(str, self._plan.params))))

    def read(self) -> Iterable[Record]:
        cursor = self._session.cursor()
        try:
            last_beat = time.monotonic()
            emitted = 0
            for data in self._driver.records_from(self._plan, cursor):
                if self._row_filter is not None and self._row_filter(data):
                    continue
                if self._change_mode_field:
                    self._apply_change_mode(data)
                yield Record(data=data, stream_name=self._stream_name)
                emitted += 1
                now = time.monotonic()
                if now - last_beat >= _HEARTBEAT_SECONDS:
                    # A LOG message is a protocol message, so this also keeps the
                    # platform's maxSecondsBetweenMessages budget from expiring
                    # during a long SAP extraction.
                    logger.info("%s: %d records read so far.", self._stream_name, emitted)
                    last_beat = now
        except Exception as exc:
            # The CDK calls ensure_at_least_one_state_emitted() even for a stream
            # that raised, so a server-side position would otherwise advance past
            # rows that were never emitted.
            if self._cursor is not None:
                self._cursor.mark_failed()
            raise traced(f"Failed reading {self._stream_name}", exc, stream_name=self._stream_name) from exc

    def _apply_change_mode(self, data: dict[str, Any]) -> None:
        """Turn an ODP delete marker into an Airbyte CDC tombstone.

        Only 'D' is reliable. A DELTAINIT row arrives with the marker NULL rather
        than 'C', and byElement-tracked sources report inserts as updates, so
        everything that is not 'D' is an upsert.
        """
        marker = data.get(self._change_mode_field)
        data[CDC_DELETED_AT] = (
            time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
            if isinstance(marker, str) and marker.strip().upper() == "D"
            else None
        )


class ErplPartitionGenerator(PartitionGenerator):
    def __init__(
        self,
        stream_name: str,
        session: ErplSession,
        driver: ProtocolDriver,
        sap_object: SapObject,
        incremental: bool,
        state: Mapping[str, Any],
        row_filter: Any | None = None,
        cursor: Any | None = None,
    ) -> None:
        self._stream_name = stream_name
        self._session = session
        self._driver = driver
        self._object = sap_object
        self._incremental = incremental
        self._state = state
        self._row_filter = row_filter
        self._cursor = cursor

    def generate(self) -> Iterable[Partition]:
        try:
            prepare = getattr(self._driver, "prepare", None)
            if prepare is not None:
                prepare(self._session, self._object, self._state)
            plans = self._driver.read_plans(
                self._session, self._object, incremental=self._incremental, state=self._state
            )
        except Exception:
            # Failing to restore the position must not read as "no changes".
            self._mark_cursor_failed()
            raise
        change_field = self._object.change_mode_field if self._incremental else None
        for plan in plans:
            yield ErplPartition(
                self._stream_name,
                self._session,
                plan,
                change_field,
                self._driver,
                row_filter=self._row_filter,
                cursor=self._cursor,
            )

    def _mark_cursor_failed(self) -> None:
        if self._cursor is not None:
            self._cursor.mark_failed()


class SapStream(DefaultStream):
    """A DefaultStream that can advertise incremental without a cursor *field*.

    ODP's position is a server-side subscription, so there is no comparable
    column in the record. `DefaultStream.as_airbyte_stream` only offers
    incremental when a CursorField is set, so the flag is applied here instead.
    """

    def __init__(
        self,
        *args: Any,
        supports_incremental: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._supports_incremental = supports_incremental

    def as_airbyte_stream(self) -> AirbyteStream:
        stream = super().as_airbyte_stream()
        if self._supports_incremental and SyncMode.incremental not in stream.supported_sync_modes:
            stream.supported_sync_modes.append(SyncMode.incremental)
            stream.source_defined_cursor = True
        return stream


def build_stream(
    session: ErplSession,
    driver: ProtocolDriver,
    sap_object: SapObject,
    cursor: Cursor,
    incremental: bool,
    state: Mapping[str, Any],
    row_filter: Any | None = None,
    namespace: str | None = None,
) -> SapStream:
    return SapStream(
        partition_generator=ErplPartitionGenerator(
            sap_object.name,
            session,
            driver,
            sap_object,
            incremental,
            state,
            row_filter,
            cursor=cursor,
        ),
        name=sap_object.name,
        json_schema=declare_cdc_column(sap_object.json_schema, sap_object),
        primary_key=_flatten_primary_key(sap_object.primary_key),
        cursor_field=None,
        logger=logger,
        cursor=cursor,
        namespace=namespace,
        supports_incremental=sap_object.supports_incremental,
    )


def _flatten_primary_key(primary_key: Sequence[Sequence[str]] | None) -> list[str]:
    return [part[0] for part in primary_key or [] if part]
