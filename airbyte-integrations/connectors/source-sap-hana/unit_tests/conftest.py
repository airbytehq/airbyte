"""Test fixtures: a fake SAP HANA backed by SQLite.

SQLite can ATTACH databases under the names SYS and SAPHANADB, so the connector's real SQL
(SYS.TABLES, "SAPHANADB"."ACDOCA", ... NULLS FIRST, qmark params) runs unchanged.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
from decimal import Decimal
from typing import Any

import pytest
from hdbcli import dbapi

pytest_plugins = ["airbyte_cdk.test.standard_tests.pytest_hooks"]

# hdbcli binds Decimal natively; teach SQLite to do the same.
sqlite3.register_adapter(Decimal, lambda d: int(d) if d == d.to_integral_value() else float(d))

SYS_DDL = """
CREATE TABLE SYS.SCHEMAS (SCHEMA_NAME TEXT);
CREATE TABLE SYS.TABLES (SCHEMA_NAME TEXT, TABLE_NAME TEXT, IS_TEMPORARY TEXT);
CREATE TABLE SYS.VIEWS (SCHEMA_NAME TEXT, VIEW_NAME TEXT);
CREATE TABLE SYS.TABLE_COLUMNS (SCHEMA_NAME TEXT, TABLE_NAME TEXT, COLUMN_NAME TEXT, POSITION INT,
                                DATA_TYPE_NAME TEXT, IS_NULLABLE TEXT);
CREATE TABLE SYS.VIEW_COLUMNS (SCHEMA_NAME TEXT, VIEW_NAME TEXT, COLUMN_NAME TEXT, POSITION INT,
                               DATA_TYPE_NAME TEXT, IS_NULLABLE TEXT);
CREATE TABLE SYS.M_TABLES (SCHEMA_NAME TEXT, TABLE_NAME TEXT, RECORD_COUNT INT, TABLE_SIZE INT);
CREATE TABLE SYS.CONSTRAINTS (SCHEMA_NAME TEXT, TABLE_NAME TEXT, COLUMN_NAME TEXT, POSITION INT,
                              IS_PRIMARY_KEY TEXT);
"""


class FakeHana:
    """Holds the SQLite database and failure-injection knobs."""

    def __init__(self) -> None:
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.lock = threading.RLock()  # the connector may read streams from several threads
        self.db.execute("ATTACH ':memory:' AS SYS")
        self.db.execute("ATTACH ':memory:' AS SAPHANADB")
        self.db.executescript(SYS_DDL)
        self.db.execute("CREATE TABLE DUMMY (DUMMY TEXT)")
        self.db.execute("INSERT INTO DUMMY VALUES ('X')")
        self.db.execute("INSERT INTO SYS.SCHEMAS VALUES ('SAPHANADB')")
        self.connect_calls: list[dict[str, Any]] = []
        self.executed: list[tuple[str, list[Any]]] = []
        # Raise "connection down" after this many rows have been fetched, once per entry.
        self.fail_after_rows: list[int] = []
        self.fail_on_connect = 0

    def add_table(self, name: str, columns: list[tuple[str, str]], rows: list[tuple], pk: list[str] = (), view: bool = False):
        cols_sql = ", ".join(f'"{c}"' for c, _ in columns)
        self.db.execute(f'CREATE TABLE SAPHANADB."{name}" ({cols_sql})')
        if rows:
            self.db.executemany(f'INSERT INTO SAPHANADB."{name}" VALUES ({", ".join("?" for _ in columns)})', rows)
        if view:
            self.db.execute("INSERT INTO SYS.VIEWS VALUES ('SAPHANADB', ?)", [name])
        else:
            self.db.execute("INSERT INTO SYS.TABLES VALUES ('SAPHANADB', ?, 'FALSE')", [name])
            self.db.execute("INSERT INTO SYS.M_TABLES VALUES ('SAPHANADB', ?, ?, ?)", [name, len(rows), 1000 * len(rows)])
        target = "VIEW_COLUMNS" if view else "TABLE_COLUMNS"
        for pos, (col, typ) in enumerate(columns, 1):
            self.db.execute(f"INSERT INTO SYS.{target} VALUES ('SAPHANADB', ?, ?, ?, ?, 'TRUE')", [name, col, pos, typ])
        for pos, col in enumerate(pk, 1):
            self.db.execute("INSERT INTO SYS.CONSTRAINTS VALUES ('SAPHANADB', ?, ?, ?, 'TRUE')", [name, col, pos])

    def connect(self, **kwargs: Any) -> FakeConnection:
        self.connect_calls.append(kwargs)
        if self.fail_on_connect:
            self.fail_on_connect -= 1
            raise dbapi.Error(-10709, "Connection failed (RTE:[89006] System call 'connect' failed)")
        return FakeConnection(self)


class FakeConnection:
    def __init__(self, hana: FakeHana):
        self.hana = hana

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.hana)

    def close(self) -> None:
        pass


class FakeCursor:
    def __init__(self, hana: FakeHana):
        self.hana = hana
        self._cursor = hana.db.cursor()
        self._fetched = 0
        self._fail_at: int | None = None

    def execute(self, sql: str, params: list[Any]) -> None:
        with self.hana.lock:
            self._execute(sql, params)

    def _execute(self, sql: str, params: list[Any]) -> None:
        self.hana.executed.append((sql, list(params)))
        try:
            self._sqlite_execute(sql, params)
        except sqlite3.OperationalError as error:
            # Surface SQLite errors the way hdbcli reports the equivalent HANA errors.
            text = str(error)
            code = 259 if "no such table" in text else 260 if "no such column" in text else 257
            raise dbapi.ProgrammingError(code, text) from error

    def _sqlite_execute(self, sql: str, params: list[Any]) -> None:
        # Failures are injected only into data reads, never into SYS catalog queries.
        if 'FROM "SAPHANADB".' in sql and self.hana.fail_after_rows:
            self._fail_at = self.hana.fail_after_rows.pop(0)
        self._cursor.execute(sql, params)

    def fetchall(self) -> list[tuple]:
        with self.hana.lock:
            return self._cursor.fetchall()

    def fetchmany(self, size: int) -> list[tuple]:
        with self.hana.lock:
            rows = self._cursor.fetchmany(size)
        if self._fail_at is not None and self._fetched + len(rows) > self._fail_at:
            rows = rows[: self._fail_at - self._fetched]
            if not rows:
                raise dbapi.OperationalError(-10807, "Connection down: [89008] Socket closed by peer")
        self._fetched += len(rows)
        return rows

    def close(self) -> None:
        self._cursor.close()


@pytest.fixture
def hana(monkeypatch: pytest.MonkeyPatch) -> FakeHana:
    fake = FakeHana()
    monkeypatch.setattr(dbapi, "connect", fake.connect)
    return fake


@pytest.fixture
def config() -> dict[str, Any]:
    return {
        "host": "hana.example.com",
        "port": 30015,
        "username": "AIRBYTE",
        "password": "secret",
        "schemas": ["SAPHANADB"],
        "fetch_size": 2,
        "checkpoint_interval": 1,
        "max_retries": 3,
        "retry_wait_seconds": 0,
    }


@pytest.fixture
def logger() -> logging.Logger:
    return logging.getLogger("airbyte")
