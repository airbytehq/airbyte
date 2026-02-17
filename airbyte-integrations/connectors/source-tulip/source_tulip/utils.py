# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared utility functions for Tulip connector.

Ported from the Fivetran connector reference implementation, adapted
for Airbyte JSON Schema types.
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Mapping, Optional


logger = logging.getLogger("airbyte")

API_VERSION = "v3"
CURSOR_OVERLAP_SECONDS = 60

SYSTEM_FIELD_NAMES = ["id", "_createdAt", "_updatedAt", "_sequenceNumber"]

SYSTEM_FIELDS_SCHEMA = {
    "id": {"type": ["null", "string"]},
    "_createdAt": {"type": ["null", "string"], "format": "date-time"},
    "_updatedAt": {"type": ["null", "string"], "format": "date-time"},
    "_sequenceNumber": {"type": ["null", "integer"]},
}

TULIP_TO_JSON_SCHEMA = {
    "integer": {"type": ["null", "integer"]},
    "float": {"type": ["null", "number"]},
    "boolean": {"type": ["null", "boolean"]},
    "timestamp": {"type": ["null", "string"], "format": "date-time"},
    "datetime": {"type": ["null", "string"], "format": "date-time"},
    "interval": {"type": ["null", "integer"]},
    "user": {"type": ["null", "string"]},
}

DEFAULT_JSON_SCHEMA_TYPE = {"type": ["null", "string"]}


def generate_column_name(field_id: str, field_label: Optional[str] = None) -> str:
    """Generate Snowflake-friendly column name from Tulip field ID and label.

    Combines the human-readable label with the field ID to create unique,
    descriptive column names in the format: label__id (e.g., customer_name__rqoqm).

    Ported exactly from the Fivetran connector.

    Args:
        field_id: Tulip field ID (required, unique identifier).
        field_label: Tulip field label (human-readable name).

    Returns:
        Snowflake-compatible column name with format label__id.
    """
    if field_label and field_label.strip():
        label = field_label.strip().lower()
        label = label.replace(" ", "_").replace("-", "_")
        label = re.sub(r"[^a-z0-9_]", "", label)
        label = re.sub(r"_+", "_", label)
        label = label.strip("_")

        if label and label[0].isdigit():
            label = f"field_{label}"

        if not label:
            label = field_id.lower()
    else:
        label = field_id.lower()

    clean_id = field_id.lower()
    clean_id = re.sub(r"[^a-z0-9_]", "", clean_id)

    column_name = f"{label}__{clean_id}"

    if not column_name or column_name[0].isdigit():
        column_name = f"field_{column_name}"

    return column_name


def map_tulip_type_to_json_schema(tulip_type: str) -> Dict[str, Any]:
    """Map a Tulip data type to a JSON Schema type definition.

    Always includes "null" in type arrays since Tulip fields can be null.

    Args:
        tulip_type: Tulip field data type string.

    Returns:
        JSON Schema type definition dict.
    """
    return TULIP_TO_JSON_SCHEMA.get(tulip_type, DEFAULT_JSON_SCHEMA_TYPE).copy()


def build_api_url(
    subdomain: str,
    workspace_id: Optional[str],
    table_id: str,
    endpoint_type: str = "",
) -> str:
    """Build Tulip API URL with optional workspace routing.

    Args:
        subdomain: Tulip instance subdomain.
        workspace_id: Workspace ID for workspace-scoped requests.
        table_id: Table ID.
        endpoint_type: Endpoint path segment; use '' for table metadata
            or 'records' for table data.

    Returns:
        Fully constructed API URL.
    """
    base_url = f"https://{subdomain}.tulip.co/api/{API_VERSION}"
    if workspace_id:
        return f"{base_url}/w/{workspace_id}/tables/{table_id}/{endpoint_type}".rstrip("/")
    return f"{base_url}/tables/{table_id}/{endpoint_type}".rstrip("/")


def build_tables_url(subdomain: str, workspace_id: Optional[str]) -> str:
    """Build URL for listing all Tulip tables.

    Args:
        subdomain: Tulip instance subdomain.
        workspace_id: Optional workspace ID.

    Returns:
        URL for the tables-listing endpoint.
    """
    base_url = f"https://{subdomain}.tulip.co/api/{API_VERSION}"
    if workspace_id:
        return f"{base_url}/w/{workspace_id}/tables"
    return f"{base_url}/tables"


def build_field_mapping(table_metadata: Mapping[str, Any]) -> Dict[str, str]:
    """Build mapping from Tulip field IDs to human-readable column names.

    Skips system fields (id, _createdAt, _updatedAt, _sequenceNumber)
    since those are passed through with their original names.

    Args:
        table_metadata: Table metadata from Tulip API.

    Returns:
        Mapping of field_id -> column_name.
    """
    field_mapping: Dict[str, str] = {}
    for field in table_metadata.get("columns", []):
        field_id = field["name"]
        if field_id in SYSTEM_FIELD_NAMES:
            continue
        field_label = field.get("label", "")
        column_name = generate_column_name(field_id, field_label)
        field_mapping[field_id] = column_name
    return field_mapping


def build_allowed_fields(table_metadata: Mapping[str, Any]) -> List[str]:
    """Build list of non-tableLink field IDs for API requests.

    Excludes tableLink fields to reduce database load on Tulip API.
    Always includes system fields required for sync operations.

    Args:
        table_metadata: Table metadata from Tulip API.

    Returns:
        Field IDs to request, excluding tableLink types.
    """
    allowed_fields = list(SYSTEM_FIELD_NAMES)
    excluded_fields = []

    for field in table_metadata.get("columns", []):
        field_id = field["name"]
        field_type = field.get("dataType", {}).get("type")

        if field_id in allowed_fields:
            continue

        if field_type == "tableLink":
            excluded_fields.append(field_id)
            continue

        allowed_fields.append(field_id)

    if excluded_fields:
        logger.info(f"Excluding {len(excluded_fields)} tableLink fields: {excluded_fields}")

    return allowed_fields


def transform_record(record: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
    """Transform Tulip record field IDs to human-readable column names.

    System fields (id, _createdAt, _updatedAt, _sequenceNumber) are
    passed through with their original names. Custom field IDs are
    mapped using the field_mapping dict.

    Args:
        record: Raw record from Tulip API.
        field_mapping: Mapping of field_id -> column_name.

    Returns:
        Transformed record with human-readable column names.
    """
    transformed: Dict[str, Any] = {}
    for field_id, value in record.items():
        if field_id in field_mapping:
            column_name = field_mapping[field_id]
        else:
            column_name = field_id
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        transformed[column_name] = value
    return transformed


def adjust_cursor_for_overlap(cursor: Optional[str]) -> Optional[str]:
    """Adjust cursor timestamp by subtracting the overlap window.

    Subtracts CURSOR_OVERLAP_SECONDS (60s) from cursor to account for
    concurrent updates that may have occurred during previous sync.

    Args:
        cursor: ISO 8601 timestamp string with optional Z suffix.

    Returns:
        Adjusted cursor timestamp, or None if input is empty.
    """
    if not cursor:
        return None

    clean_cursor = cursor.replace("Z", "+00:00")
    cursor_dt = datetime.fromisoformat(clean_cursor)
    cursor_dt = cursor_dt - timedelta(seconds=CURSOR_OVERLAP_SECONDS)
    return cursor_dt.isoformat().replace("+00:00", "Z")
