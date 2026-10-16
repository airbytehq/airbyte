# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Reads a single configured stream from SAP HANA.

Three read strategies:

* **resumable full refresh** (tables with a primary key): keyset pagination ordered by the primary key.
  A checkpoint is emitted after every page and a dropped connection resumes right after the last
  emitted row, without duplicates.
* **plain full refresh** (no primary key, or disabled): a single streamed SELECT.
* **incremental**: cursor-based, ordered by the cursor column, resuming from the last cursor value
  whose rows have all been emitted.
"""

from __future__ import annotations

import contextlib
import logging
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteStream,
    StreamDescriptor,
    SyncMode,
    Type,
)

from .client import HanaClient, describe_error, is_retryable, qualified_name, quote_identifier
from .discovery import DiscoveredTable
from .type_mapping import CURSOR_TYPES, ValueConverter, cursor_param_parser


# Same markers the Airbyte CDK emits at the end of full refresh streams.
NO_CURSOR_STATE = {"__ab_no_cursor_state_message": True}
FULL_REFRESH_COMPLETE_STATE = {"__ab_full_refresh_sync_complete": True}


class StreamReadError(Exception):
    """A configuration or data problem that makes a stream unreadable (not transient)."""


def keyset_predicate(key_columns: Sequence[str], last: Sequence[Any]) -> tuple[str, list[Any]]:
    """(k1, k2, ...) > (v1, v2, ...) expanded into OR/AND form (HANA has no row-value comparison).

    (k1 > ?) OR (k1 = ? AND k2 > ?) OR (k1 = ? AND k2 = ? AND k3 > ?) ...
    """
    disjuncts: list[str] = []
    params: list[Any] = []
    for i, column in enumerate(key_columns):
        terms = [f"{quote_identifier(key_columns[j])} = ?" for j in range(i)] + [f"{quote_identifier(column)} > ?"]
        params.extend(last[: i + 1])
        disjuncts.append("(" + " AND ".join(terms) + ")")
    return "(" + " OR ".join(disjuncts) + ")", params


class StreamReader:
    def __init__(
        self,
        client: HanaClient,
        converter: ValueConverter,
        logger: logging.Logger,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.client = client
        self.config = client.config
        self.converter = converter
        self.logger = logger
        self._sleep = sleep

    # ------------------------------------------------------------------ public

    def read(
        self,
        configured: ConfiguredAirbyteStream,
        table: DiscoveredTable,
        state: Mapping[str, Any] | None,
    ) -> Iterator[AirbyteMessage]:
        columns = self._selected_columns(configured, table)
        state = state or {}
        incremental = configured.sync_mode == SyncMode.incremental
        cursor_field = list(configured.cursor_field or []) or ([table.default_cursor_field] if table.default_cursor_field else [])
        if incremental and not cursor_field:
            # Clients such as PyAirbyte request incremental for every stream that supports it; without a
            # user-chosen cursor there is nothing to be incremental on, so read the whole table instead.
            self.logger.warning(
                f"Incremental sync requested for {table.schema}.{table.name} without a cursor field: "
                "falling back to a full refresh of the stream."
            )
            incremental = False
        if incremental:
            yield from self._read_incremental(cursor_field, table, columns, state)
        elif self.is_resumable(table):
            yield from self._read_full_refresh_keyset(table, columns, state)
        else:
            yield from self._read_full_refresh(table, columns)

    def is_resumable(self, table: DiscoveredTable) -> bool:
        return self.config.resumable_full_refresh and bool(table.primary_key)

    # ------------------------------------------------------------ full refresh

    def _read_full_refresh(self, table: DiscoveredTable, columns: list[str]) -> Iterator[AirbyteMessage]:
        where, params = self._where(table, [])
        sql = f"{self._base_select(table, columns)}{where}"
        attempt = 0
        while True:
            emitted = 0
            try:
                for row in self._execute(sql, params):
                    yield self._record(table, columns, row)
                    emitted += 1
                break
            except Exception as error:  # noqa: BLE001
                # Without an ordering key a full refresh cannot resume mid-stream without duplicating rows,
                # so only failures that happen before the first record are retried here.
                if emitted or not is_retryable(error) or attempt >= self.config.max_retries:
                    raise
                attempt += 1
                self._log_retry(table, error, attempt)
                self._sleep(self.config.retry_wait_seconds)
        yield self._state(table, NO_CURSOR_STATE)

    def _read_full_refresh_keyset(self, table: DiscoveredTable, columns: list[str], state: Mapping[str, Any]) -> Iterator[AirbyteMessage]:
        key = list(table.primary_key)
        columns = columns + [k for k in key if k not in columns]
        key_idx = [columns.index(k) for k in key]
        parsers = [cursor_param_parser(self._column_type(table, k)) for k in key]

        last: tuple[Any, ...] | None = None
        saved = state.get("primary_key")
        if isinstance(saved, Mapping) and set(saved) == set(key):
            last = tuple(parse(saved[k]) for parse, k in zip(parsers, key, strict=True))
            self.logger.info(f"Resuming full refresh of {table.schema}.{table.name} after key {dict(saved)}")

        page_size = self.config.full_refresh_page_size
        order_by = " ORDER BY " + ", ".join(quote_identifier(k) for k in key)
        attempt = 0
        while True:
            extra: list[tuple[str, list[Any]]] = [keyset_predicate(key, last)] if last is not None else []
            where, params = self._where(table, extra)
            sql = f"{self._base_select(table, columns)}{where}{order_by} LIMIT {page_size}"
            last_at_start = last
            in_page = 0
            try:
                for row in self._execute(sql, params):
                    yield self._record(table, columns, row)
                    last = tuple(row[i] for i in key_idx)
                    in_page += 1
            except Exception as error:  # noqa: BLE001
                if not is_retryable(error):
                    raise
                if last != last_at_start:
                    attempt = 0  # progress was made since the last failure: reset the retry budget
                if attempt >= self.config.max_retries:
                    raise
                attempt += 1
                self._log_retry(table, error, attempt)
                if last is not None:
                    yield self._key_state(table, key, last)
                self._sleep(self.config.retry_wait_seconds)
                continue
            if in_page:
                yield self._key_state(table, key, last)  # type: ignore[arg-type]
            if in_page < page_size:
                break
        yield self._state(table, FULL_REFRESH_COMPLETE_STATE)

    # ------------------------------------------------------------- incremental

    def _read_incremental(
        self,
        cursor_field: list[str],
        table: DiscoveredTable,
        columns: list[str],
        state: Mapping[str, Any],
    ) -> Iterator[AirbyteMessage]:
        cursor_name = self._cursor_field(cursor_field, table)
        if cursor_name not in columns:
            columns = [*columns, cursor_name]
        cursor_idx = columns.index(cursor_name)

        lower_bound: Any = None
        if state.get("cursor_field") == cursor_name and state.get("cursor") is not None:
            lower_bound = cursor_param_parser(self._column_type(table, cursor_name))(state["cursor"])
        elif state.get("cursor_field") not in (None, cursor_name):
            self.logger.warning(
                f"Cursor field of {table.schema}.{table.name} changed from {state.get('cursor_field')!r} "
                f"to {cursor_name!r}: ignoring saved state and re-reading the whole table."
            )

        cursor_sql = quote_identifier(cursor_name)
        order_by = f" ORDER BY {cursor_sql} ASC NULLS FIRST"

        current: Any = None  # cursor value of the rows being emitted right now
        completed: Any = None  # largest cursor value whose rows have *all* been emitted
        since_checkpoint = 0
        attempt = 0
        while True:
            bound = completed if completed is not None else lower_bound
            extra = [(f"{cursor_sql} > ?", [bound])] if bound is not None else []
            where, params = self._where(table, extra)
            sql = f"{self._base_select(table, columns)}{where}{order_by}"
            completed_at_start = completed
            try:
                for row in self._execute(sql, params):
                    value = row[cursor_idx]
                    if value is not None and value != current:
                        if current is not None:
                            completed = current
                            if since_checkpoint >= self.config.checkpoint_interval:
                                yield self._cursor_state(table, cursor_name, completed)
                                since_checkpoint = 0
                        current = value
                    yield self._record(table, columns, row)
                    since_checkpoint += 1
                break
            except Exception as error:  # noqa: BLE001
                if not is_retryable(error):
                    raise
                if completed != completed_at_start:
                    attempt = 0  # progress was made since the last failure: reset the retry budget
                if attempt >= self.config.max_retries:
                    raise
                attempt += 1
                self._log_retry(table, error, attempt)
                if completed is not None:
                    yield self._cursor_state(table, cursor_name, completed)
                    since_checkpoint = 0
                self._sleep(self.config.retry_wait_seconds)

        if current is not None:
            yield self._cursor_state(table, cursor_name, current)
        elif lower_bound is not None:
            yield self._state(table, {"cursor_field": cursor_name, "cursor": state["cursor"]})
        else:
            yield self._state(table, {"cursor_field": cursor_name, "cursor": None})

    # ----------------------------------------------------------------- helpers

    def _execute(self, sql: str, params: Sequence[Any]) -> Iterator[Sequence[Any]]:
        self.logger.info(f"Executing: {sql}")
        conn = self.client.connect()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, list(params))
                while True:
                    rows = cursor.fetchmany(self.config.fetch_size)
                    if not rows:
                        return
                    yield from rows
            finally:
                cursor.close()
        finally:
            with contextlib.suppress(Exception):  # the connection may already be dead after a network error
                conn.close()

    def _base_select(self, table: DiscoveredTable, columns: Sequence[str]) -> str:
        return f"SELECT {', '.join(quote_identifier(c) for c in columns)} FROM {qualified_name(table.schema, table.name)}"

    def _where(self, table: DiscoveredTable, extra: Sequence[tuple[str, list[Any]]]) -> tuple[str, list[Any]]:
        """WHERE clause combining the user-defined stream filter with the strategy's own predicates."""
        clauses: list[str] = []
        params: list[Any] = []
        user_filter = self.config.stream_filter(table.schema, table.name)
        if user_filter:
            clauses.append(f"({user_filter})")
        for clause, clause_params in extra:
            clauses.append(clause)
            params.extend(clause_params)
        return (" WHERE " + " AND ".join(clauses), params) if clauses else ("", params)

    @staticmethod
    def _column_type(table: DiscoveredTable, name: str) -> str:
        column = table.column(name)
        if column is None:
            raise StreamReadError(f"Column {name!r} does not exist in {table.schema}.{table.name}")
        return column.hana_type

    @staticmethod
    def _selected_columns(configured: ConfiguredAirbyteStream, table: DiscoveredTable) -> list[str]:
        """Columns selected in the configured catalog, in table order (all columns if nothing is listed)."""
        properties = (configured.stream.json_schema or {}).get("properties") or {}
        columns = [c.name for c in table.columns if not properties or c.name in properties]
        if not columns:
            raise StreamReadError(f"None of the selected columns exist in {table.schema}.{table.name}")
        return columns

    @staticmethod
    def _cursor_field(cursor_field: list[str], table: DiscoveredTable) -> str:
        if len(cursor_field) != 1:
            raise StreamReadError(
                f"Incremental sync of {table.schema}.{table.name} requires exactly one top-level cursor field, got {cursor_field}"
            )
        column = table.column(cursor_field[0])
        if column is None:
            raise StreamReadError(f"Cursor field {cursor_field[0]!r} does not exist in {table.schema}.{table.name}")
        if column.hana_type.upper() not in CURSOR_TYPES:
            raise StreamReadError(
                f"Column {column.name!r} of type {column.hana_type} cannot be used as a cursor "
                f"(supported: {', '.join(sorted(CURSOR_TYPES))})"
            )
        return column.name

    def _record(self, table: DiscoveredTable, columns: Sequence[str], row: Sequence[Any]) -> AirbyteMessage:
        convert = self.converter
        return AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=table.name,
                namespace=table.schema,
                data={name: convert(value) for name, value in zip(columns, row, strict=True)},
                emitted_at=int(time.time() * 1000),
            ),
        )

    def _cursor_state(self, table: DiscoveredTable, cursor_name: str, value: Any) -> AirbyteMessage:
        return self._state(table, {"cursor_field": cursor_name, "cursor": self.converter(value)})

    def _key_state(self, table: DiscoveredTable, key: Sequence[str], last: Sequence[Any]) -> AirbyteMessage:
        return self._state(table, {"primary_key": {k: self.converter(v) for k, v in zip(key, last, strict=True)}})

    @staticmethod
    def _state(table: DiscoveredTable, data: Mapping[str, Any]) -> AirbyteMessage:
        return AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name=table.name, namespace=table.schema),
                    stream_state=AirbyteStateBlob(**data),
                ),
            ),
        )

    def _log_retry(self, table: DiscoveredTable, error: BaseException, attempt: int) -> None:
        self.logger.warning(
            f"Reading {table.schema}.{table.name} failed with a transient error ({describe_error(error)}); "
            f"reconnecting in {self.config.retry_wait_seconds}s (retry {attempt}/{self.config.max_retries})"
        )
