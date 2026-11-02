#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import hashlib
import logging
import re
import uuid
from typing import Any, Dict, List, Mapping, Optional

import orjson

from destination_meilisearch.client import MeiliClient


logger = logging.getLogger("airbyte")

# Attribute holding the ID of each document, which is the primary key of the
# indexes written by this destination.
PRIMARY_KEY = "_ab_pk"
# Attribute holding the generation of the sync that wrote a document, which is
# used to delete the documents of earlier generations after a refresh.
GENERATION_ID = "_airbyte_generation_id"
CDC_DELETED_AT = "_ab_cdc_deleted_at"

# Document IDs may only contain alphanumerics, '-' and '_', and are limited to
# 511 bytes.
# See https://www.meilisearch.com/docs/learn/resources/known_limitations#length-of-primary-key-values
VALID_DOCUMENT_ID = re.compile(r"[A-Za-z0-9_-]{1,511}")
# Index UIDs have the same alphabet, and are limited to 400 bytes.
MAX_INDEX_UID_BYTES = 400
INVALID_INDEX_UID_CHARS = re.compile(r"[^A-Za-z0-9_-]")

# Meilisearch rejects payloads larger than its http-payload-size-limit, which
# defaults to 100MB.
MAX_BATCH_BYTES = 50 * 1024 * 1024


def index_uid(name: str, namespace: Optional[str] = None) -> str:
    """Returns the index UID for a stream, replacing characters which are not
    allowed in index UIDs with underscores."""
    full = f"{namespace}_{name}" if namespace else name
    return INVALID_INDEX_UID_CHARS.sub("_", full)[:MAX_INDEX_UID_BYTES]


def document_id(key_values: List[Any]) -> str:
    """Returns the document ID for the values of a record's primary key.

    A single primary key value which is a valid document ID is used as-is, so
    that documents can be looked up by their natural key. Other keys are
    replaced by a hash of their values.
    """
    if len(key_values) == 1:
        value = key_values[0]
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
        if isinstance(value, str) and VALID_DOCUMENT_ID.fullmatch(value):
            return value
    digest = hashlib.sha256(orjson.dumps(key_values, option=orjson.OPT_SORT_KEYS)).hexdigest()
    return f"h_{digest}"


def extract_key(data: Mapping[str, Any], primary_key: List[List[str]]) -> List[Any]:
    values = []
    for path in primary_key:
        value: Any = data
        for part in path:
            value = value.get(part) if isinstance(value, Mapping) else None
        if value is None:
            raise ValueError(f"Record is missing a value for primary key field '{'.'.join(path)}'")
        values.append(value)
    return values


class StreamWriter:
    """Buffers the records of a stream and sends them to its index in batches.

    Additions and deletions are sent as separate requests. Meilisearch processes
    the tasks of an index in the order they are enqueued, so the buffer is
    flushed whenever the kind of operation changes, which keeps the operations
    on a document in order.
    """

    def __init__(
        self,
        client: MeiliClient,
        index: str,
        batch_size: int,
        primary_key: Optional[List[List[str]]] = None,
        generation_id: Optional[int] = None,
    ):
        self.client = client
        self.index = index
        self.batch_size = batch_size
        # Records are deduplicated by their primary key only if one is set.
        self.primary_key = primary_key
        self.generation_id = generation_id

        # Documents to add or replace, by ID. A later record for the same ID
        # replaces an earlier one that is still buffered.
        self._documents: Dict[str, bytes] = {}
        self._document_bytes = 0
        self._deletes: List[str] = []

        self._warned_reserved = False

        self.pending_tasks: List[int] = []
        self.records_written = 0
        self.records_deleted = 0

    def write(self, data: Mapping[str, Any]) -> None:
        if self.primary_key:
            doc_id = document_id(extract_key(data, self.primary_key))
            if data.get(CDC_DELETED_AT) is not None:
                self._delete(doc_id)
                return
        else:
            doc_id = str(uuid.uuid4())

        if not self._warned_reserved and (PRIMARY_KEY in data or GENERATION_ID in data):
            logger.warning(
                f"Records written to index '{self.index}' have a '{PRIMARY_KEY}' or '{GENERATION_ID}' field, which is replaced by the value the destination sets"
            )
            self._warned_reserved = True

        doc = dict(data)
        doc[PRIMARY_KEY] = doc_id
        if self.generation_id is not None:
            doc[GENERATION_ID] = self.generation_id
        encoded = orjson.dumps(doc) + b"\n"

        if self._deletes:
            self._flush_deletes()
        previous = self._documents.get(doc_id)
        if previous is not None:
            self._document_bytes -= len(previous)
        self._documents[doc_id] = encoded
        self._document_bytes += len(encoded)

        if len(self._documents) >= self.batch_size or self._document_bytes >= MAX_BATCH_BYTES:
            self._flush_documents()

    def _delete(self, doc_id: str) -> None:
        if self._documents:
            self._flush_documents()
        self._deletes.append(doc_id)
        if len(self._deletes) >= self.batch_size:
            self._flush_deletes()

    def flush(self) -> None:
        # At most one of these is non-empty.
        self._flush_documents()
        self._flush_deletes()

    def _flush_documents(self) -> None:
        if not self._documents:
            return
        payload = b"".join(self._documents.values())
        count = len(self._documents)
        index = self.client.client.index(self.index)
        logger.info(f"Sending {count} documents ({len(payload)} bytes) to index '{self.index}'")
        self.pending_tasks.append(
            self.client.enqueue(
                f"add documents to index '{self.index}'",
                lambda: index.add_documents_ndjson(payload, primary_key=PRIMARY_KEY),
            )
        )
        self.records_written += count
        self._documents = {}
        self._document_bytes = 0

    def _flush_deletes(self) -> None:
        if not self._deletes:
            return
        ids = self._deletes
        index = self.client.client.index(self.index)
        logger.info(f"Deleting {len(ids)} documents from index '{self.index}'")
        self.pending_tasks.append(
            self.client.enqueue(
                f"delete documents from index '{self.index}'",
                lambda: index.delete_documents(ids),
            )
        )
        self.records_deleted += len(ids)
        self._deletes = []
