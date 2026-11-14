# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Airbyte source connector for SAP HANA."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from dataclasses import replace
from functools import partial
from typing import Any

from hdbcli import dbapi

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteEstimateTraceMessage,
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamStatus,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    EstimateType,
    FailureType,
    Status,
    SyncMode,
    TraceType,
    Type,
)
from airbyte_cdk.sources import Source
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .client import INVALID_TABLE_NAME, HanaClient, describe_error, qualified_name
from .concurrency import interleave
from .config import HanaConfig
from .discovery import CatalogDiscoverer, DiscoveredTable, StreamSettingsError
from .reader import StreamReader
from .ssh_tunnel import SshTunnel, TunnelConfig
from .type_mapping import ValueConverter


StreamKey = tuple[str | None, str]  # (namespace, name)


class SourceSapHana(Source):
    @contextmanager
    def _session(self, config: Mapping[str, Any], logger: logging.Logger) -> Iterator[HanaClient]:
        """A HanaClient for the duration of one command, routed through the SSH tunnel if one is configured."""
        hana = HanaConfig.from_mapping(config)
        tunnel_config = TunnelConfig.from_mapping(config.get("tunnel_method"))
        if tunnel_config is None:
            yield HanaClient(hana, logger)
            return
        with SshTunnel(tunnel_config, hana.host, hana.port, logger) as tunnel:
            properties = dict(hana.connection_properties)
            if hana.encrypt:
                # The TLS certificate names the real HANA host, not the local end of the tunnel.
                properties.setdefault("sslHostNameInCertificate", hana.host)
            yield HanaClient(replace(hana, host="127.0.0.1", port=tunnel.local_port, connection_properties=properties), logger)

    # ------------------------------------------------------------------- check

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            with self._session(config, logger) as client:
                client.query_all("SELECT 1 FROM DUMMY")
                missing = self._missing_schemas(client)
                if missing:
                    return AirbyteConnectionStatus(status=Status.FAILED, message=self._missing_schemas_message(client, missing))
                problems = self._validate_stream_settings(client)
                if problems:
                    return AirbyteConnectionStatus(status=Status.FAILED, message="Invalid stream settings: " + " | ".join(problems))
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as error:  # noqa: BLE001
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Unable to connect to SAP HANA: {describe_error(error)}")

    @staticmethod
    def _missing_schemas(client: HanaClient) -> list[str]:
        schemas = client.config.schemas
        placeholders = ", ".join("?" for _ in schemas)
        sql = f"SELECT SCHEMA_NAME FROM SYS.SCHEMAS WHERE SCHEMA_NAME IN ({placeholders})"
        found = {row[0] for row in client.query_all(sql, schemas)}
        return [s for s in schemas if s not in found]

    @staticmethod
    def _validate_stream_settings(client: HanaClient) -> list[str]:
        """Runs every per-stream condition with LIMIT 0, so typos surface at check time instead of mid-sync."""
        problems: list[str] = []
        for (schema, table), settings in client.config.stream_settings.items():
            label = f"{schema}.{table}" if schema else table
            where = f" WHERE ({settings.condition})" if settings.condition else ""
            found = False
            for candidate in [schema] if schema else client.config.schemas:
                try:
                    client.query_all(f"SELECT 1 FROM {qualified_name(candidate, table)}{where} LIMIT 0")
                    found = True
                except dbapi.Error as error:
                    if getattr(error, "errorcode", None) == INVALID_TABLE_NAME:
                        continue  # not in this schema
                    found = True
                    problems.append(f"{label}: {describe_error(error)}")
            if not found:
                problems.append(f"{label}: table or view not found in schemas {', '.join(client.config.schemas)}")
        return problems

    @staticmethod
    def _missing_schemas_message(client: HanaClient, missing: list[str]) -> str:
        return f"Schemas not found or not visible to user {client.config.username}: {', '.join(missing)}"

    # ---------------------------------------------------------------- discover

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        with self._session(config, logger) as client:
            missing = self._missing_schemas(client)
            if missing:
                raise AirbyteTracedException(message=self._missing_schemas_message(client, missing), failure_type=FailureType.config_error)
            try:
                tables = CatalogDiscoverer(client).discover()
            except StreamSettingsError as error:
                raise AirbyteTracedException(message=str(error), failure_type=FailureType.config_error) from error
        logger.info(f"Discovered {len(tables)} tables/views")
        cfg = client.config
        return AirbyteCatalog(streams=[t.to_airbyte_stream(cfg.decimal_as_string, cfg.resumable_full_refresh) for t in tables])

    # -------------------------------------------------------------------- read

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: list[AirbyteStateMessage] | None = None,
    ) -> Iterator[AirbyteMessage]:
        failed: list[str] = []
        with self._session(config, logger) as client:
            discoverer = CatalogDiscoverer(client)
            converter = ValueConverter(client.config.decimal_as_string, client.config.strip_nul_characters)
            reader = StreamReader(client, converter, logger)
            stream_states = self._parse_state(state or [])

            def stream_messages(configured: ConfiguredAirbyteStream) -> Iterator[AirbyteMessage]:
                return self._read_stream(configured, discoverer, reader, stream_states, logger, failed)

            workers = min(client.config.max_concurrent_streams, len(catalog.streams))
            if workers <= 1:
                for configured in catalog.streams:
                    yield from stream_messages(configured)
            else:
                logger.info(f"Reading {len(catalog.streams)} streams with {workers} concurrent workers")
                yield from interleave([partial(stream_messages, c) for c in catalog.streams], workers)

        if failed:
            raise AirbyteTracedException(
                message=f"{len(failed)} stream(s) failed: {', '.join(failed)}. See logs for details.",
                failure_type=FailureType.system_error,
            )

    @staticmethod
    def _read_stream(
        configured: ConfiguredAirbyteStream,
        discoverer: CatalogDiscoverer,
        reader: StreamReader,
        stream_states: Mapping[StreamKey, MutableMapping[str, Any]],
        logger: logging.Logger,
        failed: list[str],
    ) -> Iterator[AirbyteMessage]:
        """All messages of one stream, including its status traces; failures are recorded in `failed`, not raised."""
        stream = configured.stream
        label = f"{stream.namespace}.{stream.name}" if stream.namespace else stream.name
        yield stream_status_message(stream, AirbyteStreamStatus.STARTED)
        try:
            if not stream.namespace:
                raise AirbyteTracedException(
                    message=f"Stream {stream.name} has no namespace (schema); re-run discovery.",
                    failure_type=FailureType.config_error,
                )
            table = discoverer.discover_one(stream.namespace, stream.name)
            if table is None:
                raise AirbyteTracedException(
                    message=f"Table or view {label} no longer exists or is not readable by the configured user.",
                    failure_type=FailureType.config_error,
                )
            logger.info(f"Syncing {label} ({configured.sync_mode.value})")
            estimate = SourceSapHana._row_estimate(discoverer.client, table, configured)
            if estimate is not None:
                yield estimate
            running = False
            count = 0
            for message in reader.read(configured, table, stream_states.get((stream.namespace, stream.name))):
                if not running:
                    yield stream_status_message(stream, AirbyteStreamStatus.RUNNING)
                    running = True
                if message.record is not None:
                    count += 1
                yield message
            logger.info(f"Finished {label}: {count} records")
            yield stream_status_message(stream, AirbyteStreamStatus.COMPLETE)
        except Exception as error:  # noqa: BLE001 - one broken stream must not stop the others
            logger.error(f"Stream {label} failed: {describe_error(error)}", exc_info=True)
            failed.append(label)
            yield stream_status_message(stream, AirbyteStreamStatus.INCOMPLETE)

    @staticmethod
    def _row_estimate(client: HanaClient, table: DiscoveredTable, configured: ConfiguredAirbyteStream) -> AirbyteMessage | None:
        """Row count from SYS.M_TABLES for unfiltered full refreshes, so the Airbyte UI can show sync progress."""
        if configured.sync_mode != SyncMode.full_refresh or table.kind != "TABLE" or client.config.stream_filter(table.schema, table.name):
            return None
        try:
            rows = client.query_all(
                "SELECT SUM(RECORD_COUNT), SUM(TABLE_SIZE) FROM SYS.M_TABLES WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?",
                [table.schema, table.name],
            )
        except Exception:  # noqa: BLE001 - estimates are best effort (M_TABLES may not be visible to the user)
            return None
        if not rows or rows[0][0] is None:
            return None
        return AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.ESTIMATE,
                emitted_at=time.time() * 1000,
                # The Airbyte platform rejects estimates without a byte estimate ("getByteEstimate(...) must not be null").
                estimate=AirbyteEstimateTraceMessage(
                    name=table.name,
                    namespace=table.schema,
                    type=EstimateType.STREAM,
                    row_estimate=int(rows[0][0]),
                    byte_estimate=int(rows[0][1] or 0),
                ),
            ),
        )

    @staticmethod
    def _parse_state(state: list[AirbyteStateMessage]) -> dict[StreamKey, MutableMapping[str, Any]]:
        parsed: dict[StreamKey, MutableMapping[str, Any]] = {}
        for message in state:
            if message.type == AirbyteStateType.STREAM and message.stream is not None:
                descriptor = message.stream.stream_descriptor
                blob = message.stream.stream_state
                parsed[(descriptor.namespace, descriptor.name)] = dict(blob.__dict__) if blob is not None else {}
        return parsed
