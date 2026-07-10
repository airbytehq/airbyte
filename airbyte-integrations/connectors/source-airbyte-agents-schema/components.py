#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Custom components for `source-airbyte-agents-schema`.

This connector turns Airbyte's own configuration metadata into an
[Agents Schema](https://github.com/dbt-labs/agents_schema)-shaped dataset. Given a single
destination actor id, it enumerates every connection landing in that destination, and emits:

- `airbyte_stream` (the `AGENTS.DBT_MODEL` analog): one record per active/selected stream, carrying
  the logical stream identity plus a best-effort *physical destination table name* derived from the
  connection's namespace/prefix configuration.
- `root` (the `AGENTS.ROOT` analog): a small self-describing index plus free-form markdown `skill/…`
  rows telling a downstream SQL agent how Airbyte lands data (namespace/prefix mapping, the
  `_airbyte_*` metadata columns, raw-vs-typed-final tables, dedup-vs-append semantics).

Both streams read the public API `connections` endpoint. The two pieces of logic that genuinely
cannot be expressed declaratively — multi-record expansion (one connection -> N stream rows) and
physical-table-name derivation — live here as custom `RecordExtractor`s.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


def _resolve_namespace(connection: Mapping[str, Any], stream: Mapping[str, Any]) -> Optional[str]:
    """Resolve the destination schema/namespace a stream lands in.

    Mirrors Airbyte's namespace resolution: `source` uses the stream's own namespace, `destination`
    falls back to the destination's default schema (`None` here), and `custom_format` substitutes the
    stream namespace into `namespaceFormat`. Returns `None` when the destination default should apply.
    """
    definition = connection.get("namespaceDefinition")
    stream_namespace = stream.get("namespace")
    if definition == "source":
        return stream_namespace
    if definition == "destination":
        return None
    if definition == "custom_format":
        namespace_format = connection.get("namespaceFormat") or ""
        return namespace_format.replace("${SOURCE_NAMESPACE}", stream_namespace or "")
    return stream_namespace


def _physical_table_name(connection: Mapping[str, Any], stream_name: str) -> str:
    """Derive the best-effort physical (typed final) table name for a stream.

    Applies the connection `prefix` to the stream name. Final identifier casing/truncation is
    destination-specific (Snowflake upper-cases, BigQuery preserves case, etc.); that normalization is
    intentionally NOT applied here and is documented in the `root` guidance instead.
    """
    prefix = connection.get("prefix") or ""
    return f"{prefix}{stream_name}"


def _iter_target_connections(records: Iterable[Mapping[str, Any]], destination_id: str) -> Iterable[Mapping[str, Any]]:
    """Yield only connections that land in the requested destination actor."""
    for connection in records:
        if connection.get("destinationId") == destination_id:
            yield connection


@dataclass
class AgentsStreamExtractor(RecordExtractor):
    """Explode the `connections` response into one record per selected stream.

    Scoped to `config['destination_id']`: only connections whose `destinationId` matches are expanded,
    so a token with visibility into multiple workspaces never leaks sibling-destination streams.
    """

    config: Mapping[str, Any]
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[str, Any]]:
        destination_id = self.config["destination_id"]
        body = response.json()
        connections = body.get("data", []) if isinstance(body, Mapping) else []
        for connection in _iter_target_connections(connections, destination_id):
            configurations = connection.get("configurations") or {}
            for stream in configurations.get("streams", []) or []:
                stream_name = stream.get("name")
                if not stream_name:
                    continue
                selected_fields = [
                    f.get("fieldPath", [None])[0] if isinstance(f, Mapping) else f for f in (stream.get("selectedFields") or [])
                ]
                yield {
                    "connection_id": connection.get("connectionId"),
                    "connection_name": connection.get("name"),
                    "workspace_id": connection.get("workspaceId"),
                    "source_id": connection.get("sourceId"),
                    "destination_id": connection.get("destinationId"),
                    "stream_name": stream_name,
                    "stream_namespace": stream.get("namespace"),
                    "sync_mode": stream.get("syncMode"),
                    "primary_key": stream.get("primaryKey"),
                    "cursor_field": stream.get("cursorField"),
                    "selected_fields": [f for f in selected_fields if f],
                    "destination_namespace": _resolve_namespace(connection, stream),
                    "destination_table_name": _physical_table_name(connection, stream_name),
                    "prefix": connection.get("prefix"),
                    "namespace_definition": connection.get("namespaceDefinition"),
                    "namespace_format": connection.get("namespaceFormat"),
                    "connection_status": connection.get("status"),
                }


_LANDING_CONVENTIONS_SKILL = """\
# Querying Airbyte-landed data

Airbyte writes each selected stream to a table in the destination. Use `AGENTS.AIRBYTE_STREAM` to map
a logical stream to its physical table:

- **Schema/namespace** comes from the connection's namespace configuration
  (`destination_namespace` in `AGENTS.AIRBYTE_STREAM`). When it is null, the destination's default
  schema is used.
- **Table name** is `prefix` + stream name (`destination_table_name`). Final identifier casing and
  truncation are destination-specific — Snowflake upper-cases unquoted identifiers, BigQuery
  preserves case, Postgres lower-cases. Match casing accordingly when you write SQL.

## Destinations V2 layout

Modern Airbyte destinations write **typed final tables** named after the stream (the
`destination_table_name` above) alongside raw tables in a separate internal schema
(commonly `airbyte_internal`, table `<namespace>_raw__stream_<name>`). Prefer the typed final table.

Every row carries Airbyte metadata columns:

- `_airbyte_raw_id` — unique id for the record.
- `_airbyte_extracted_at` — when the record was read from the source.
- `_airbyte_meta` — JSON with per-row typing/change info.
- `_airbyte_generation_id` — increments across refreshes.

## Sync mode semantics

- **append / append_dedup**: `append_dedup` keeps one row per primary key (latest by cursor); plain
  `append` may contain historical duplicates — deduplicate on `primary_key` ordered by
  `cursor_field` (or `_airbyte_extracted_at`) when you need the current state.
- **full_refresh|overwrite**: the table is fully replaced each sync; no dedup needed.

Consult `primary_key` and `cursor_field` in `AGENTS.AIRBYTE_STREAM` to write correct dedup SQL.
"""


@dataclass
class AgentsRootExtractor(RecordExtractor):
    """Synthesize the `AGENTS.ROOT` index + guidance rows for the target destination.

    Emits `(provider, key, content)` rows: a JSON `index` summarizing the destination's stream/table
    inventory (from the first page of connections) plus static `skill/…` markdown guidance. The
    authoritative, fully-paginated per-stream list lives in the `airbyte_stream` stream.
    """

    config: Mapping[str, Any]
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[str, Any]]:
        destination_id = self.config["destination_id"]
        body = response.json()
        connections = body.get("data", []) if isinstance(body, Mapping) else []

        tables: list[dict[str, Any]] = []
        connection_ids: set[str] = set()
        for connection in _iter_target_connections(connections, destination_id):
            connection_ids.add(connection.get("connectionId"))
            configurations = connection.get("configurations") or {}
            for stream in configurations.get("streams", []) or []:
                stream_name = stream.get("name")
                if not stream_name:
                    continue
                tables.append(
                    {
                        "stream_name": stream_name,
                        "destination_namespace": _resolve_namespace(connection, stream),
                        "destination_table_name": _physical_table_name(connection, stream_name),
                    }
                )

        index = {
            "description": (
                "Agents Schema materialized from Airbyte configuration metadata for destination "
                f"{destination_id}. See AGENTS.AIRBYTE_STREAM for the full stream-to-table mapping."
            ),
            "destination_id": destination_id,
            "connection_count": len(connection_ids),
            "stream_count": len(tables),
            "tables": tables,
            "extensions": ["AIRBYTE_STREAM"],
        }

        yield {"provider": "airbyte", "key": "index", "content": json.dumps(index, default=str)}
        yield {
            "provider": "airbyte",
            "key": "skill/query-airbyte-landed-data",
            "content": _LANDING_CONVENTIONS_SKILL,
        }
