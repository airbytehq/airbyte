# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Typed view over the connector configuration (see spec.json)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StreamSettings:
    condition: str | None = None
    cursor_field: str | None = None
    primary_key: tuple[str, ...] = ()


@dataclass(frozen=True)
class HanaConfig:
    host: str
    port: int
    username: str
    password: str
    schemas: list[str]
    database_name: str | None = None
    table_name_patterns: list[str] = field(default_factory=list)
    include_views: bool = False
    encrypt: bool = False
    ssl_validate_certificate: bool = True
    ssl_trust_store: str | None = None
    compress: bool = True
    connection_properties: dict[str, str] = field(default_factory=dict)
    fetch_size: int = 10_000
    checkpoint_interval: int = 10_000
    max_retries: int = 5
    retry_wait_seconds: int = 30
    decimal_as_string: bool = False
    strip_nul_characters: bool = True
    resumable_full_refresh: bool = True
    full_refresh_page_size: int = 100_000
    max_concurrent_streams: int = 1
    # {(schema or None, table): settings}
    stream_settings: dict[tuple[str | None, str], StreamSettings] = field(default_factory=dict)

    def settings_for(self, schema: str, table: str) -> StreamSettings:
        """Per-stream settings: a SCHEMA.TABLE entry wins over a bare TABLE entry."""
        return self.stream_settings.get((schema, table)) or self.stream_settings.get((None, table)) or StreamSettings()

    def stream_filter(self, schema: str, table: str) -> str | None:
        return self.settings_for(schema, table).condition

    @classmethod
    def from_mapping(cls, config: Mapping[str, Any]) -> HanaConfig:
        return cls(
            host=config["host"],
            port=int(config.get("port", 30015)),
            username=config["username"],
            password=config["password"],
            schemas=list(config["schemas"]),
            database_name=config.get("database_name") or None,
            table_name_patterns=list(config.get("table_name_patterns") or []),
            include_views=bool(config.get("include_views", False)),
            encrypt=bool(config.get("encrypt", False)),
            ssl_validate_certificate=bool(config.get("ssl_validate_certificate", True)),
            ssl_trust_store=config.get("ssl_trust_store") or None,
            compress=bool(config.get("compress", True)),
            connection_properties=parse_connection_properties(config.get("connection_properties")),
            fetch_size=int(config.get("fetch_size", 10_000)),
            checkpoint_interval=int(config.get("checkpoint_interval", 10_000)),
            max_retries=int(config.get("max_retries", 5)),
            retry_wait_seconds=int(config.get("retry_wait_seconds", 30)),
            decimal_as_string=config.get("decimal_handling", "number") == "string",
            strip_nul_characters=bool(config.get("strip_nul_characters", True)),
            resumable_full_refresh=bool(config.get("resumable_full_refresh", True)),
            full_refresh_page_size=int(config.get("full_refresh_page_size", 100_000)),
            max_concurrent_streams=max(1, int(config.get("max_concurrent_streams", 1))),
            stream_settings=parse_stream_settings(config.get("stream_settings")),
        )


def parse_connection_properties(raw: str | None) -> dict[str, str]:
    """Parse 'k1=v1;k2=v2' into a dict, ignoring blanks."""
    if not raw:
        return {}
    props: dict[str, str] = {}
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        key, sep, value = part.partition("=")
        if not sep or not key.strip():
            raise ValueError(f"Invalid connection property '{part}': expected key=value")
        props[key.strip()] = value.strip()
    return props


def parse_stream_settings(raw: Any) -> dict[tuple[str | None, str], StreamSettings]:
    """Parse [{"stream": "SCHEMA.TABLE" | "TABLE", "condition"?, "cursor_field"?, "primary_key"?}] into a lookup dict."""
    settings: dict[tuple[str | None, str], StreamSettings] = {}
    for entry in raw or []:
        stream = (entry.get("stream") or "").strip()
        if not stream:
            raise ValueError(f"Invalid stream settings {entry!r}: 'stream' is required")
        condition = (entry.get("condition") or "").strip() or None
        if condition and ";" in condition:
            raise ValueError(f"Invalid condition for {stream}: ';' is not allowed in a filter condition")
        cursor_field = (entry.get("cursor_field") or "").strip() or None
        primary_key = tuple(c.strip() for c in entry.get("primary_key") or [] if c and c.strip())
        if not (condition or cursor_field or primary_key):
            raise ValueError(f"Stream settings for {stream} must set at least one of condition, cursor_field, primary_key")
        schema, dot, table = stream.rpartition(".")
        key = (schema, table) if dot else (None, stream)
        if key in settings:
            raise ValueError(f"Duplicate stream settings for {stream}")
        settings[key] = StreamSettings(condition=condition, cursor_field=cursor_field, primary_key=primary_key)
    return settings
