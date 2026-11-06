# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Thin wrapper around hdbcli: connection handling, retry classification, identifier quoting."""

from __future__ import annotations

import contextlib
import logging
import time
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from typing import Any, TypeVar

from hdbcli import dbapi

from .config import HanaConfig


T = TypeVar("T")

# hdbcli error codes that indicate the session/socket is gone and a reconnect may succeed.
# -10709 connection failed, -10807 connection down, -10821 session not connected,
# -10108 session has been reconnected (statement lost), -10813 socket closed,
# -10810 connection closed by peer, 4 cannot allocate enough memory (transient on busy systems).
RETRYABLE_ERROR_CODES = frozenset({-10709, -10807, -10821, -10108, -10813, -10810, 4})
INVALID_TABLE_NAME = 259
_RETRYABLE_MESSAGE_FRAGMENTS = ("connection down", "connection failed", "socket closed", "connection reset")


def quote_identifier(name: str) -> str:
    """Quote a HANA identifier. SAP names such as /BIC/AZSALES00 must always be quoted."""
    return '"' + name.replace('"', '""') + '"'


def qualified_name(schema: str, table: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(table)}"


def is_retryable(error: BaseException) -> bool:
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True
    if isinstance(error, dbapi.Error):
        code = getattr(error, "errorcode", None)
        if code in RETRYABLE_ERROR_CODES:
            return True
        text = str(getattr(error, "errortext", "") or error).lower()
        return any(fragment in text for fragment in _RETRYABLE_MESSAGE_FRAGMENTS)
    return False


def describe_error(error: BaseException) -> str:
    if isinstance(error, dbapi.Error):
        code = getattr(error, "errorcode", None)
        text = getattr(error, "errortext", None) or str(error)
        return f"[{code}] {text}" if code is not None else text
    return str(error)


class HanaClient:
    def __init__(self, config: HanaConfig, logger: logging.Logger, sleep: Callable[[float], None] = time.sleep):
        self.config = config
        self.logger = logger
        self._sleep = sleep

    def connect_kwargs(self) -> dict[str, Any]:
        cfg = self.config
        kwargs: dict[str, Any] = {
            "address": cfg.host,
            "port": cfg.port,
            "user": cfg.username,
            "password": cfg.password,
        }
        if cfg.database_name:
            kwargs["databaseName"] = cfg.database_name
        if cfg.compress:
            kwargs["compress"] = True
        if cfg.encrypt:
            kwargs["encrypt"] = True
            kwargs["sslValidateCertificate"] = cfg.ssl_validate_certificate
            if cfg.ssl_trust_store:
                kwargs["sslTrustStore"] = cfg.ssl_trust_store
        # User-supplied properties win: they are the escape hatch for anything not in the spec.
        kwargs.update(cfg.connection_properties)
        return kwargs

    def connect(self) -> dbapi.Connection:
        return self.with_retries(lambda: dbapi.connect(**self.connect_kwargs()), "connect")

    @contextmanager
    def connection(self) -> Iterator[dbapi.Connection]:
        """Single connection attempt; callers wrap the whole unit of work in with_retries()."""
        conn = dbapi.connect(**self.connect_kwargs())
        try:
            yield conn
        finally:
            with contextlib.suppress(Exception):  # closing a dead connection must never mask the real error
                conn.close()

    def with_retries(self, fn: Callable[[], T], what: str) -> T:
        attempt = 0
        while True:
            try:
                return fn()
            except Exception as error:  # noqa: BLE001
                if not is_retryable(error) or attempt >= self.config.max_retries:
                    raise
                attempt += 1
                self.logger.warning(
                    f"{what} failed with a transient error ({describe_error(error)}); "
                    f"retry {attempt}/{self.config.max_retries} in {self.config.retry_wait_seconds}s"
                )
                self._sleep(self.config.retry_wait_seconds)

    def query_all(self, sql: str, params: Sequence[Any] = ()) -> list[tuple]:
        def run() -> list[tuple]:
            with self.connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql, list(params))
                    return [tuple(row) for row in cursor.fetchall()]
                finally:
                    cursor.close()

        return self.with_retries(run, "catalog query")
