"""Catalog discovery from the SAP HANA SYS catalog views."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from airbyte_cdk.models import AirbyteStream, SyncMode

from .client import HanaClient
from .type_mapping import json_schema_for


class StreamSettingsError(ValueError):
    """The user's per-stream settings do not match the table definition."""


@dataclass(frozen=True)
class Column:
    name: str
    hana_type: str
    nullable: bool = True


@dataclass
class DiscoveredTable:
    schema: str
    name: str
    kind: str  # "TABLE" or "VIEW"
    columns: list[Column] = field(default_factory=list)
    primary_key: list[str] = field(default_factory=list)
    default_cursor_field: str | None = None

    def column(self, name: str) -> Column | None:
        return next((c for c in self.columns if c.name == name), None)

    def to_airbyte_stream(self, decimal_as_string: bool = False, resumable_full_refresh: bool = True) -> AirbyteStream:
        properties = {c.name: json_schema_for(c.hana_type, decimal_as_string) for c in self.columns}
        return AirbyteStream(
            name=self.name,
            namespace=self.schema,
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "additionalProperties": True,
                "properties": properties,
            },
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
            source_defined_cursor=False,
            default_cursor_field=[self.default_cursor_field] if self.default_cursor_field else None,
            source_defined_primary_key=[[c] for c in self.primary_key] or None,
            is_resumable=resumable_full_refresh and bool(self.primary_key),
        )


def _in_clause(column: str, values: Sequence[str]) -> str:
    return f"{column} IN ({', '.join('?' for _ in values)})"


def _like_clause(column: str, patterns: Sequence[str]) -> str:
    return "(" + " OR ".join(f"{column} LIKE ?" for _ in patterns) + ")"


def _filters(schemas: Sequence[str], patterns: Sequence[str], name_column: str) -> tuple[str, list[Any]]:
    clauses = [_in_clause("SCHEMA_NAME", schemas)]
    params: list[Any] = list(schemas)
    if patterns:
        clauses.append(_like_clause(name_column, patterns))
        params.extend(patterns)
    return " AND ".join(clauses), params


class CatalogDiscoverer:
    def __init__(self, client: HanaClient):
        self.client = client
        self.config = client.config

    def discover(self, schemas: Sequence[str] | None = None, patterns: Sequence[str] | None = None) -> list[DiscoveredTable]:
        schemas = list(schemas if schemas is not None else self.config.schemas)
        patterns = list(patterns if patterns is not None else self.config.table_name_patterns)

        objects: dict[tuple[str, str], DiscoveredTable] = {}
        for schema, name in self._list_tables(schemas, patterns):
            objects[(schema, name)] = DiscoveredTable(schema=schema, name=name, kind="TABLE")
        if self.config.include_views:
            for schema, name in self._list_views(schemas, patterns):
                objects[(schema, name)] = DiscoveredTable(schema=schema, name=name, kind="VIEW")
        if not objects:
            return []

        for schema, name, column, data_type, nullable in self._list_columns(schemas, patterns):
            table = objects.get((schema, name))
            if table is not None:
                table.columns.append(Column(name=column, hana_type=data_type, nullable=nullable == "TRUE"))

        for (schema, name), pk in self._primary_keys(schemas, patterns).items():
            table = objects.get((schema, name))
            if table is not None:
                table.primary_key = pk

        tables = sorted((t for t in objects.values() if t.columns), key=lambda t: (t.schema, t.name))
        for table in tables:
            self._apply_stream_settings(table)
        return tables

    def _apply_stream_settings(self, table: DiscoveredTable) -> None:
        """Applies user-defined primary key overrides and default cursors, validating the column names."""
        settings = self.config.settings_for(table.schema, table.name)
        for column in (*settings.primary_key, *([settings.cursor_field] if settings.cursor_field else [])):
            if table.column(column) is None:
                raise StreamSettingsError(f"Stream settings for {table.schema}.{table.name} reference unknown column {column!r}")
        if settings.primary_key:
            table.primary_key = list(settings.primary_key)
        if settings.cursor_field:
            table.default_cursor_field = settings.cursor_field

    def discover_one(self, schema: str, name: str) -> DiscoveredTable | None:
        """Re-reads the definition of a single object (used at read time to get authoritative column types)."""
        # LIKE with an exact name is safe: '_' and '%' only broaden the match, the exact filter below narrows it.
        for table in self.discover([schema], [name]):
            if table.schema == schema and table.name == name:
                return table
        return None

    def _list_tables(self, schemas: Sequence[str], patterns: Sequence[str]) -> list[tuple]:
        where, params = _filters(schemas, patterns, "TABLE_NAME")
        sql = f"SELECT SCHEMA_NAME, TABLE_NAME FROM SYS.TABLES WHERE {where} AND IS_TEMPORARY = 'FALSE'"
        return self.client.query_all(sql, params)

    def _list_views(self, schemas: Sequence[str], patterns: Sequence[str]) -> list[tuple]:
        where, params = _filters(schemas, patterns, "VIEW_NAME")
        sql = f"SELECT SCHEMA_NAME, VIEW_NAME FROM SYS.VIEWS WHERE {where}"
        return self.client.query_all(sql, params)

    def _list_columns(self, schemas: Sequence[str], patterns: Sequence[str]) -> list[tuple]:
        where, params = _filters(schemas, patterns, "TABLE_NAME")
        sql = (
            "SELECT SCHEMA_NAME, TABLE_NAME, COLUMN_NAME, DATA_TYPE_NAME, IS_NULLABLE "
            f"FROM SYS.TABLE_COLUMNS WHERE {where} ORDER BY SCHEMA_NAME, TABLE_NAME, POSITION"
        )
        rows = self.client.query_all(sql, params)
        if self.config.include_views:
            where, params = _filters(schemas, patterns, "VIEW_NAME")
            sql = (
                "SELECT SCHEMA_NAME, VIEW_NAME, COLUMN_NAME, DATA_TYPE_NAME, IS_NULLABLE "
                f"FROM SYS.VIEW_COLUMNS WHERE {where} ORDER BY SCHEMA_NAME, VIEW_NAME, POSITION"
            )
            rows += self.client.query_all(sql, params)
        return rows

    def _primary_keys(self, schemas: Sequence[str], patterns: Sequence[str]) -> dict[tuple[str, str], list[str]]:
        where, params = _filters(schemas, patterns, "TABLE_NAME")
        sql = (
            "SELECT SCHEMA_NAME, TABLE_NAME, COLUMN_NAME FROM SYS.CONSTRAINTS "
            f"WHERE {where} AND IS_PRIMARY_KEY = 'TRUE' ORDER BY SCHEMA_NAME, TABLE_NAME, POSITION"
        )
        keys: dict[tuple[str, str], list[str]] = defaultdict(list)
        for schema, name, column in self.client.query_all(sql, params):
            keys[(schema, name)].append(column)
        return dict(keys)
