"""`source-sap` -- one connector, four SAP access protocols."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    Status,
    SyncMode,
)
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from source_sap.cursors import DriverStateCursor, FieldValueCursor, NoStateCursor
from source_sap.errors import config_error
from source_sap.protocols.base import ProtocolDriver, SapObject
from source_sap.protocols.bics import BicsDriver, is_grand_total_row
from source_sap.protocols.odp_odata import OdpODataDriver
from source_sap.protocols.odp_rfc import OdpRfcDriver
from source_sap.protocols.rfc import RfcDriver
from source_sap.protocols.rfc_invoke import RfcInvokeDriver
from source_sap.session import ErplSession, SessionSettings
from source_sap.streams import build_stream, declare_cdc_column

logger = logging.getLogger("airbyte")

DRIVERS: dict[str, type[ProtocolDriver]] = {
    RfcDriver.mode: RfcDriver,
    RfcInvokeDriver.mode: RfcInvokeDriver,
    BicsDriver.mode: BicsDriver,
    OdpRfcDriver.mode: OdpRfcDriver,
    OdpODataDriver.mode: OdpODataDriver,
}

DEFAULT_WORKERS = 4
MAX_WORKERS = 32  # matches the spec's maximum; each worker holds a SAP connection


class SourceSap(ConcurrentSourceAdapter):
    def __init__(
        self,
        catalog: ConfiguredAirbyteCatalog | None = None,
        config: Mapping[str, Any] | None = None,
        state: list[AirbyteStateMessage] | None = None,
    ) -> None:
        self._catalog = catalog
        self._config = config
        self._state = state
        self._message_repository: MessageRepository = InMemoryMessageRepository()
        self._session: ErplSession | None = None
        num_workers = self._num_workers(config or {})
        super().__init__(
            ConcurrentSource.create(
                num_workers=num_workers,
                initial_number_of_partitions_to_generate=max(num_workers // 2, 1),
                logger=logger,
                slice_logger=DebugSliceLogger(),
                message_repository=self._message_repository,
            )
        )

    @staticmethod
    def _num_workers(config: Mapping[str, Any]) -> int:
        """Clamp to the spec's range; a hand-edited config should not be able to
        exhaust the SAP system's work processes."""
        value = config.get("concurrency")
        if value is None or value == "":
            return DEFAULT_WORKERS
        try:
            requested = int(value)
        except (TypeError, ValueError):
            return DEFAULT_WORKERS
        return max(1, min(MAX_WORKERS, requested))

    @property
    def message_repository(self) -> MessageRepository:
        return self._message_repository

    # ---- spec / check / discover ---------------------------------------------

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        return super().spec(logger)

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> tuple[bool, Any]:
        driver = self._driver(config)
        # Says so before the connection is made, so the warning is visible even
        # when the check itself then fails.
        driver.warn_about_insecure_transport()
        with self._new_session(config, driver) as session:
            message = driver.check(session)
        logger.info(message)
        return True, None

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            self.check_connection(logger, config)
        except AirbyteTracedException as exc:
            return AirbyteConnectionStatus(status=Status.FAILED, message=exc.message)
        except Exception as exc:  # noqa: BLE001 - surface anything as a check failure
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(exc))
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        driver = self._driver(config)
        with self._new_session(config, driver) as session:
            objects = driver.discover(session)
            streams = [
                build_stream(
                    session,
                    driver,
                    obj,
                    NoStateCursor(obj.name, None, self._message_repository, ConnectorStateManager()),
                    incremental=False,
                    state={},
                ).as_airbyte_stream()
                for obj in objects
            ]
        if not streams:
            raise config_error(
                "Discovery found no SAP objects for this configuration. Check the pattern and the "
                "explicit object list, and that the SAP user is authorised to read them."
            )
        return AirbyteCatalog(streams=streams)

    # ---- read ----------------------------------------------------------------

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: list[AirbyteStateMessage] | None = None,
    ) -> Iterable[AirbyteMessage]:
        self._config = config
        self._catalog = catalog
        self._state = state
        try:
            yield from super().read(logger, config, catalog, state)
        finally:
            if self._session is not None:
                # erpl_web asserts if its connection is collected at interpreter exit.
                self._session.close()
                self._session = None

    def streams(self, config: Mapping[str, Any]) -> list[Stream]:
        driver = self._driver(config)
        session = self._shared_session(config, driver)
        state_manager = ConnectorStateManager(state=self._state or [])
        configured = {s.stream.name: s for s in (self._catalog.streams if self._catalog else [])}

        discovered = driver.discover(session)
        if self._catalog is not None:
            self._assert_all_configured_streams_found(configured, [o.name for o in discovered])

        streams: list[Stream] = []
        for obj in discovered:
            configured_stream = configured.get(obj.name)
            if self._catalog is not None and configured_stream is None:
                continue
            incremental = bool(
                configured_stream is not None
                and configured_stream.sync_mode == SyncMode.incremental
                and obj.supports_incremental
            )
            stream_state = state_manager.get_stream_state(obj.name, None)
            cursor = self._cursor(driver, session, obj, incremental, stream_state, state_manager)
            concurrent_stream = build_stream(
                session,
                driver,
                obj,
                cursor,
                incremental,
                stream_state,
                row_filter=self._row_filter(driver, obj),
            )
            streams.append(StreamFacade(concurrent_stream, _LegacyStreamShim(obj), cursor, DebugSliceLogger(), logger))
        return streams

    @staticmethod
    def _assert_all_configured_streams_found(configured: Mapping[str, Any], discovered: Sequence[str]) -> None:
        """A configured stream that no longer exists must fail, not sync empty.

        Renaming a table or revoking an authorization would otherwise show up as
        a successful sync that produced no records.
        """
        missing = sorted(set(configured) - set(discovered))
        if not missing:
            return
        raise config_error(
            f"Configured stream(s) no longer found in SAP: {', '.join(missing)}. "
            "They may have been renamed, the selection pattern may have changed, or the "
            "SAP user may have lost authorization. Refresh the schema, or fix the source "
            "configuration."
        )

    def _cursor(
        self,
        driver: ProtocolDriver,
        session: ErplSession,
        obj: SapObject,
        incremental: bool,
        stream_state: Mapping[str, Any],
        state_manager: ConnectorStateManager,
    ):
        if not incremental:
            return NoStateCursor(obj.name, None, self._message_repository, state_manager)
        cursor_field = obj.meta.get("cursor_field")
        if cursor_field:
            return FieldValueCursor(
                obj.name, None, self._message_repository, state_manager, str(cursor_field), stream_state
            )
        return DriverStateCursor(
            obj.name, None, self._message_repository, state_manager, driver, session, obj, stream_state
        )

    @staticmethod
    def _row_filter(driver: ProtocolDriver, obj: SapObject):
        """BW appends a grand-total row to every BICS result; drop it."""
        if not isinstance(driver, BicsDriver):
            return None
        # Applied even with no row axis configured: BW appends the total to every
        # result, so leaving it in the stream is never right.
        row_axis = list(obj.meta.get("row_axis") or [])
        return lambda record: is_grand_total_row(record, row_axis)

    # ---- plumbing ------------------------------------------------------------

    def _driver(self, config: Mapping[str, Any]) -> ProtocolDriver:
        protocol = config.get("protocol") or {}
        mode = str(protocol.get("mode") or "").strip()
        driver_class = DRIVERS.get(mode)
        if driver_class is None:
            raise config_error(f"Unknown protocol {mode!r}. Choose one of: {', '.join(sorted(DRIVERS))}.")
        return driver_class(config)

    def _new_session(self, config: Mapping[str, Any], driver: ProtocolDriver) -> ErplSession:
        return ErplSession(
            config,
            extensions=driver.required_extensions,
            settings=SessionSettings(num_workers=self._num_workers(config)),
        )

    def _shared_session(self, config: Mapping[str, Any], driver: ProtocolDriver) -> ErplSession:
        if self._session is None:
            self._session = self._new_session(config, driver)
        return self._session


class _LegacyStreamShim(Stream):
    """`StreamFacade` needs a legacy Stream for the properties it proxies.

    Nothing reads records through it -- the concurrent stream does that -- but
    the facade asks it for name, primary key and schema.
    """

    def __init__(self, sap_object: SapObject) -> None:
        self._object = sap_object

    @property
    def name(self) -> str:
        return self._object.name

    @property
    def primary_key(self) -> Any:
        return self._object.primary_key

    def get_json_schema(self) -> Mapping[str, Any]:
        # Through `declare_cdc_column`, because this is the schema `discover`
        # publishes and the records carry the tombstone.
        return declare_cdc_column(self._object.json_schema, self._object)

    def read_records(self, *args: Any, **kwargs: Any):  # pragma: no cover - never called
        raise NotImplementedError("Records are read through the concurrent stream.")
