#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import hashlib
import re
from collections.abc import Mapping
from logging import getLogger
from typing import Any, Dict, List
from uuid import uuid4

from meilisearch import Client


logger = getLogger("airbyte")

# Synthetic primary-key field injected into documents when the stream's natural
# primary key cannot be used as a Meilisearch primary key (no key, composite, or
# nested). Meilisearch supports a single, flat primary-key attribute only.
INTERNAL_PK_FIELD = "_ab_pk"

# Task wait bounds. Indexing is asynchronous; we block on each batch so failures
# surface in-line and back-pressure matches Meilisearch throughput.
TASK_TIMEOUT_MS = 1_800_000  # 30 minutes
TASK_INTERVAL_MS = 200

# Meilisearch document-id constraint: integer, or string of these characters only.
VALID_STRING_ID = re.compile(r"[a-zA-Z0-9_-]+")

# id-resolution strategies, see resolve_primary_key.
ID_NATURAL = "natural"  # the source field is the Meilisearch primary key; documents pass through
ID_RANDOM = "random"  # inject INTERNAL_PK_FIELD with a random UUID (every record kept)
ID_HASH = "hash"  # inject INTERNAL_PK_FIELD with a deterministic hash of the key values


class MeiliWriter:
    """Buffers records for one stream and flushes them to a Meilisearch index.

    A writer owns exactly one index. It knows which field is the index primary
    key, how to derive each document's id, whether to replace or merge documents,
    and when to flush.
    """

    def __init__(
        self,
        client: Client,
        index_name: str,
        primary_key: str,
        id_mode: str,
        key_paths: List[List[str]],
        merge: bool,
        batch_size: int,
    ):
        self.client = client
        self.index_name = index_name
        self.primary_key = primary_key
        self.id_mode = id_mode
        self.key_paths = key_paths
        self.merge = merge
        self.batch_size = max(1, batch_size)
        self._buffer: List[Dict[str, Any]] = []
        logger.info(
            f"MeiliWriter for index '{index_name}': primary_key='{primary_key}', "
            f"id_mode='{id_mode}', merge={merge}, batch_size={self.batch_size}"
        )

    def queue_write_operation(self, data: Mapping[str, Any]) -> None:
        self._buffer.append(self._prepare(data))
        if len(self._buffer) >= self.batch_size:
            self.flush()

    def _prepare(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        """Return the document to index, injecting the synthetic id when needed."""
        if self.id_mode == ID_NATURAL:
            self._validate_natural_key(data)
            return dict(data)
        document = dict(data)
        if self.id_mode == ID_RANDOM:
            document[INTERNAL_PK_FIELD] = uuid4().hex
        else:  # ID_HASH
            document[INTERNAL_PK_FIELD] = self._hash_key(data)
        return document

    def _validate_natural_key(self, data: Mapping[str, Any]) -> None:
        """Fail per record, naming the field and value, instead of letting the whole
        Meilisearch batch task fail with an error that names neither."""
        if self.primary_key not in data:
            raise ValueError(f"Record for index '{self.index_name}' is missing primary key field '{self.primary_key}'")
        value = data[self.primary_key]
        if isinstance(value, bool) or not (isinstance(value, int) or (isinstance(value, str) and VALID_STRING_ID.fullmatch(value))):
            raise ValueError(
                f"Primary key '{self.primary_key}'={value!r} for index '{self.index_name}' is not a valid "
                f"Meilisearch document id (must be an integer or a string of only [a-zA-Z0-9_-])"
            )

    def _hash_key(self, data: Mapping[str, Any]) -> str:
        values = []
        for path in self.key_paths:
            value: Any = data
            for key in path:
                if not isinstance(value, Mapping) or key not in value:
                    raise ValueError(f"Primary key path {path} not found in record for index '{self.index_name}'")
                value = value[key]
            if value is None:
                raise ValueError(f"Primary key path {path} is null in record for index '{self.index_name}'")
            values.append(str(value))
        return hashlib.sha1(":".join(values).encode("utf-8")).hexdigest()

    def flush(self) -> None:
        if not self._buffer:
            return
        count = len(self._buffer)
        logger.info(f"Flushing {count} records to index '{self.index_name}'")
        index = self.client.index(self.index_name)
        if self.merge:
            task = index.update_documents(self._buffer, self.primary_key)
        else:
            task = index.add_documents(self._buffer, self.primary_key)
        result = self.client.wait_for_task(task.task_uid, TASK_TIMEOUT_MS, TASK_INTERVAL_MS)
        if result.status != "succeeded":
            raise RuntimeError(
                f"Meilisearch task {task.task_uid} for index '{self.index_name}' did not succeed "
                f"(status='{result.status}', error={getattr(result, 'error', None)})"
            )
        self._buffer.clear()
