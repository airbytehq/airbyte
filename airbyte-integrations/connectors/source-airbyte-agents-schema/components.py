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

Connection enumeration uses the public API `connections` endpoint, scoped server-side to the
destination's workspace by a `SubstreamPartitionRouter` (the workspace is resolved from a parent
`destination` request) and filtered to the destination id. Each connection's configured catalog is
then read per connection from the internal Config API (`web_backend/connections/get`, the same
endpoint PyAirbyte uses), which — unlike the public API — returns field-level types plus sync
freshness. `root` reads the `destinations/{id}` endpoint. The pieces of logic that genuinely cannot
be expressed declaratively — multi-record expansion (one connection -> N stream rows), typed-column
flattening, and physical-table-name derivation — live here as custom `RecordExtractor`s.

The human-facing help text surfaced through `root` (and the small helpers that render it) is kept
in the `PROMPT / DOCS CONTENT` block at the top of this module, insulated from the connector logic
below so the docs can be reviewed and iterated on without touching extraction code.

Note: annotations are intentionally NOT deferred via `from __future__ import annotations`. The
manifest-only custom-code loader `exec`s this module before registering it in `sys.modules`, and
deferred (string) annotations combined with `@dataclass` fail to resolve during that window.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


# ======================================================================================
# PROMPT / DOCS CONTENT
#
# Everything in this block is human-facing help text — the `root` stream's self-describing
# index and the free-form `skill/…` guidance an agent reads — plus the tiny helpers that
# render it. It is intentionally hoisted to the top and insulated from the connector logic
# below so these docs can be reviewed and iterated on independently of "real" code.
# ======================================================================================

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
- **Columns** (`columns`) lists each field with its JSON Schema `type`; use it to pick columns and
  reason about types without reading the table. `selected_fields` is populated only when a connection
  syncs an explicit subset (otherwise all `columns` sync).
- **Freshness** (`last_sync_status`, `last_sync_at`, `is_syncing`) tells you whether a table is
  current before you trust it — treat streams whose last sync failed or is stale with caution.

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


def _build_root_index(destination_id: str) -> dict:
    """Build the self-describing `index` payload emitted by the `root` stream.

    The index is response-independent: the authoritative per-stream/table inventory is a cross-page
    aggregation that lives in `AGENTS.AIRBYTE_STREAM`, so this just describes the dataset and points
    there rather than trying to summarize counts a per-response extractor cannot compute correctly.
    """
    return {
        "description": (
            "Agents Schema materialized from Airbyte configuration metadata for destination "
            f"{destination_id}. See AGENTS.AIRBYTE_STREAM for the full stream-to-table mapping."
        ),
        "destination_id": destination_id,
        "extensions": ["AIRBYTE_STREAM"],
    }


def _build_root_rows(destination_id: str) -> list:
    """Build the ordered `(provider, key, content)` rows the `root` stream emits."""
    return [
        {
            "provider": "airbyte",
            "key": "index",
            "content": json.dumps(_build_root_index(destination_id), default=str),
        },
        {
            "provider": "airbyte",
            "key": "skill/query-airbyte-landed-data",
            "content": _LANDING_CONVENTIONS_SKILL,
        },
    ]


# ======================================================================================
# CONNECTOR LOGIC
# ======================================================================================


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


def _selected_field_names(stream_config: Mapping[str, Any]) -> list:
    """Return the explicitly selected top-level field names, or `[]` when all fields sync."""
    if not stream_config.get("fieldSelectionEnabled"):
        return []
    names = []
    for selected in stream_config.get("selectedFields") or []:
        if not isinstance(selected, Mapping):
            continue
        path = selected.get("fieldPath") or []
        if path:
            names.append(path[0])
    return names


def _typed_columns(stream: Mapping[str, Any], stream_config: Mapping[str, Any]) -> list:
    """Flatten the stream's JSON Schema into `{name, type}` column records.

    When field selection is enabled the list is restricted to the selected top-level fields;
    otherwise every property in the catalog's JSON Schema is emitted. `type` is the raw JSON Schema
    type (typically a `["null", "<type>"]` list) and is intentionally left un-normalized.
    """
    properties = (stream.get("jsonSchema") or {}).get("properties") or {}
    selected = _selected_field_names(stream_config)
    names = selected if selected else list(properties.keys())
    columns = []
    for name in names:
        prop = properties.get(name)
        column_type = prop.get("type") if isinstance(prop, Mapping) else None
        columns.append({"name": name, "type": column_type})
    return columns


def _workspace_id(connection: Mapping[str, Any]) -> Optional[str]:
    """Resolve the workspace id from the Config API connection's source/destination actor."""
    for actor_key in ("destination", "source"):
        actor = connection.get(actor_key)
        if isinstance(actor, Mapping) and actor.get("workspaceId"):
            return actor["workspaceId"]
    return connection.get("workspaceId")


@dataclass
class AgentsStreamCatalogExtractor(RecordExtractor):
    """Explode a single Config API `web_backend/connections/get` response into per-stream records.

    Each partition is one connection landing in `config['destination_id']` (the parent
    `connections_index` stream already scopes to the destination). For every *selected* stream in the
    connection's configured catalog it emits the logical identity, the derived physical destination
    table, typed columns from the stream's JSON Schema, and connection-level sync freshness.
    """

    config: Mapping[str, Any]
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[str, Any]]:
        connection = response.json()
        if not isinstance(connection, Mapping):
            return
        workspace_id = _workspace_id(connection)
        last_sync_at = connection.get("latestSyncJobCreatedAt")
        sync_catalog = connection.get("syncCatalog") or {}
        for entry in sync_catalog.get("streams", []) or []:
            stream = entry.get("stream") or {}
            stream_config = entry.get("config") or {}
            if not stream_config.get("selected", True):
                continue
            stream_name = stream.get("name")
            if not stream_name:
                continue
            yield {
                "connection_id": connection.get("connectionId"),
                "connection_name": connection.get("name"),
                "workspace_id": workspace_id,
                "source_id": connection.get("sourceId"),
                "destination_id": connection.get("destinationId"),
                "stream_name": stream_name,
                "stream_namespace": stream.get("namespace"),
                "sync_mode": stream_config.get("syncMode"),
                "destination_sync_mode": stream_config.get("destinationSyncMode"),
                "primary_key": stream_config.get("primaryKey"),
                "cursor_field": stream_config.get("cursorField"),
                "selected_fields": _selected_field_names(stream_config),
                "columns": _typed_columns(stream, stream_config),
                "destination_namespace": _resolve_namespace(connection, stream),
                "destination_table_name": _physical_table_name(connection, stream_name),
                "prefix": connection.get("prefix"),
                "namespace_definition": connection.get("namespaceDefinition"),
                "namespace_format": connection.get("namespaceFormat"),
                "connection_status": connection.get("status"),
                "last_sync_status": connection.get("latestSyncJobStatus"),
                "last_sync_at": last_sync_at,
                "is_syncing": connection.get("isSyncing"),
            }


@dataclass
class AgentsRootExtractor(RecordExtractor):
    """Synthesize the `AGENTS.ROOT` index + guidance rows for the target destination.

    Emits the `(provider, key, content)` rows built by `_build_root_rows` (see the `PROMPT / DOCS
    CONTENT` block above). This extractor is response-independent: the full stream inventory is a
    cross-page aggregation that a per-response `RecordExtractor` cannot compute correctly, so it is
    deliberately left to the fully-paginated `airbyte_stream` stream rather than summarized here.
    """

    config: Mapping[str, Any]
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[str, Any]]:
        yield from _build_root_rows(self.config["destination_id"])
