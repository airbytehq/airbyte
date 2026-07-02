#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from psycopg2.extras import Json

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, Chunk
from airbyte_cdk.destinations.vector_db_based.utils import create_stream_identifier
from destination_opengauss_datavec.schema import MetadataColumn


HASH_LENGTH = 8
CHUNK_INDEX_WIDTH = 4
BIGINT_MIN = -(2**63)
BIGINT_MAX = 2**63 - 1


class RowBuilder:
    def __init__(self, omit_raw_text: bool):
        self.omit_raw_text = omit_raw_text

    def copy_columns(self, metadata_columns: List[MetadataColumn]) -> List[str]:
        """Return COPY column order matching rows produced by create_rows."""
        columns = ["document_id", "chunk_id"]
        if not self.omit_raw_text:
            columns.append("content")
        columns.append("embedding")
        columns.extend(column.column_name for column in metadata_columns)
        columns.extend(["_airbyte_extracted_at", "_airbyte_meta"])
        return columns

    def create_rows(self, document_chunks: List[Chunk], metadata_columns: List[MetadataColumn]) -> Iterable[Tuple[Any, ...]]:
        """Convert CDK chunks into COPY rows for the destination table."""
        generated_document_ids: Dict[int, str] = {}
        chunk_indexes_by_document_id: Dict[str, int] = {}

        for chunk in document_chunks:
            document_id = document_id_for_chunk(chunk, generated_document_ids)
            chunk_index = chunk_indexes_by_document_id.get(document_id, 0)
            chunk_indexes_by_document_id[document_id] = chunk_index + 1

            row = [document_id, chunk_id(document_id, chunk_index, chunk.page_content)]
            if not self.omit_raw_text:
                row.append(chunk.page_content)
            row.append(embedding_value(chunk.embedding))

            metadata_meta_changes = []
            for column in metadata_columns:
                value, change = metadata_value(chunk.metadata.get(column.metadata_key), column)
                row.append(value)
                if change is not None:
                    metadata_meta_changes.append(change)

            row.append(record_emitted_at(chunk))
            row.append(Json({"changes": metadata_meta_changes}))
            yield tuple(row)


def document_id_for_chunk(chunk: Chunk, generated_document_ids: Dict[int, str]) -> str:
    """Use CDK _ab_record_id in dedup mode, otherwise generate a per-record id."""
    cdk_record_id = chunk.metadata.get(METADATA_RECORD_ID_FIELD)
    if cdk_record_id is not None:
        return str(cdk_record_id)

    record_key = id(chunk.record)
    if record_key not in generated_document_ids:
        generated_document_ids[record_key] = f"{create_stream_identifier(chunk.record)}_{uuid.uuid4()}"
    return generated_document_ids[record_key]


def chunk_id(document_id: str, chunk_index: int, content: Optional[str]) -> str:
    """Build a readable chunk id from document id, index, and content hash."""
    content_hash = "0" * HASH_LENGTH
    if content is not None:
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:HASH_LENGTH]
    return f"{document_id}_{chunk_index:0{CHUNK_INDEX_WIDTH}d}_{content_hash}"


def embedding_value(embedding: Optional[List[float]]) -> str:
    """Serialize embeddings in the vector literal format accepted by DataVec."""
    if embedding is None:
        raise ValueError("Cannot index a chunk without an embedding")
    return "[" + ",".join(str(value) for value in embedding) + "]"


def record_emitted_at(chunk: Chunk) -> Optional[datetime]:
    """Convert Airbyte emitted_at milliseconds to timestamptz value."""
    emitted_at = getattr(chunk.record, "emitted_at", None)
    if emitted_at is None:
        return None
    return datetime.fromtimestamp(float(emitted_at) / 1000, timezone.utc)


def metadata_value(value: Any, column: MetadataColumn) -> Tuple[Any, Optional[Dict[str, str]]]:
    """Coerce metadata values; null bigint values that cannot fit into int64."""
    if value is None:
        return None, None

    if column.sql_type == "jsonb":
        return Json(value), None

    if column.sql_type == "bigint":
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            return None, meta_change(column.column_name, f"INT_CONVERSION_FAILED: Expected bigint value, but got {value}")
        if int_value < BIGINT_MIN or int_value > BIGINT_MAX:
            return None, meta_change(column.column_name, "BIGINT_OVERFLOW")
        return int_value, None

    if column.sql_type == "boolean":
        if isinstance(value, bool):
            return value, None
        if isinstance(value, str) and value.lower() in ("true", "false"):
            return value.lower() == "true", None
        if value in (0, 1):
            return bool(value), None
        return None, meta_change(column.column_name, f"BOOLEAN_CONVERSION_FAILED: Expected boolean value, but got {value}")

    if isinstance(value, (dict, list)):
        return json.dumps(value), None

    return value, None


def meta_change(field: str, reason: str) -> Dict[str, str]:
    """Create an _airbyte_meta change entry for nulled values."""
    return {"field": field, "change": "NULLED", "reason": reason}
