#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from logging import Logger, getLogger
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from uuid import uuid4

from meilisearch import Client
from meilisearch.errors import MeilisearchApiError

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateType,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    Type,
)
from destination_meilisearch.writer import (
    ID_HASH,
    ID_NATURAL,
    ID_RANDOM,
    INTERNAL_PK_FIELD,
    MeiliWriter,
)

logger = getLogger("airbyte")

DEFAULT_BATCH_SIZE = 1000


def get_client(config: Mapping[str, Any]) -> Client:
    return Client(config.get("host"), config.get("api_key"))


def sanitize_index_name(name: str) -> str:
    """Meilisearch index uids accept only [a-zA-Z0-9_-]."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)


def resolve_primary_key(stream: ConfiguredAirbyteStream) -> Tuple[str, str, List[List[str]]]:
    """Decide the Meilisearch primary key field and how to derive document ids.

    Returns (primary_key_field, id_mode, key_paths).

    - append always uses random ids so every emitted record is preserved.
    - a single top-level source key is used directly as the Meilisearch primary key.
    - a composite or nested key falls back to a deterministic hash in INTERNAL_PK_FIELD.
    - no key falls back to a random id in INTERNAL_PK_FIELD.
    """
    key_paths: List[List[str]] = stream.primary_key or []

    if stream.destination_sync_mode == DestinationSyncMode.append:
        return INTERNAL_PK_FIELD, ID_RANDOM, []

    if len(key_paths) == 1 and len(key_paths[0]) == 1:
        return key_paths[0][0], ID_NATURAL, key_paths

    if key_paths:
        return INTERNAL_PK_FIELD, ID_HASH, key_paths

    return INTERNAL_PK_FIELD, ID_RANDOM, []


def get_existing_primary_key(client: Client, index_name: str) -> Optional[str]:
    """Return the index's current primaryKey, or None if the index does not exist."""
    try:
        return client.get_index(index_name).primary_key
    except MeilisearchApiError as e:
        if e.code == "index_not_found":
            return None
        raise


class DestinationMeilisearch(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        client = get_client(config=config)
        batch_size = int(config.get("batch_size") or DEFAULT_BATCH_SIZE)
        merge = config.get("update_method") == "merge"

        # Distinct streams must not collide onto one index after sanitization.
        index_names: Dict[str, str] = {}
        for stream in configured_catalog.streams:
            index_name = sanitize_index_name(stream.stream.name)
            if index_name in index_names:
                raise ValueError(
                    f"Streams '{index_names[index_name]}' and '{stream.stream.name}' both map to Meilisearch "
                    f"index '{index_name}'. Rename one of the streams so the indexes stay distinct."
                )
            index_names[index_name] = stream.stream.name

        # Build one writer per configured stream and reset overwrite indexes up front.
        writers: Dict[str, MeiliWriter] = {}
        for stream in configured_catalog.streams:
            index_name = sanitize_index_name(stream.stream.name)
            primary_key, id_mode, key_paths = resolve_primary_key(stream)

            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self._reset_index(client, index_name, primary_key)
            else:
                # The primaryKey of an index cannot change while it has documents. Fail
                # up front with an actionable message instead of an opaque task error on
                # every batch (e.g. after an upgrade from v1, which always used _ab_pk).
                existing_pk = get_existing_primary_key(client, index_name)
                if existing_pk is not None and existing_pk != primary_key:
                    raise ValueError(
                        f"Index '{index_name}' already has primary key '{existing_pk}', but this sync "
                        f"resolved primary key '{primary_key}'. Meilisearch cannot change an index's "
                        f"primary key once set. Either run this stream in 'overwrite' mode once, or "
                        f"delete the index in Meilisearch, and sync again."
                    )

            writers[stream.stream.name] = MeiliWriter(
                client=client,
                index_name=index_name,
                primary_key=primary_key,
                id_mode=id_mode,
                key_paths=key_paths,
                merge=merge,
                batch_size=batch_size,
            )

        for message in input_messages:
            if message.type == Type.STATE:
                # Flush before checkpointing so acknowledged state reflects persisted
                # data. Stream-scoped state only requires that stream's writer; global
                # and legacy state require everything.
                state = message.state
                if state and state.type == AirbyteStateType.STREAM and state.stream and state.stream.stream_descriptor:
                    writer = writers.get(state.stream.stream_descriptor.name)
                    if writer:
                        writer.flush()
                else:
                    for writer in writers.values():
                        writer.flush()
                yield message
            elif message.type == Type.RECORD:
                stream = message.record.stream
                if stream not in writers:
                    logger.debug(f"Stream {stream} not in configured catalog, skipping record")
                    continue
                writers[stream].queue_write_operation(message.record.data)
            else:
                logger.info(f"Unhandled message type {message.type}")

        for writer in writers.values():
            writer.flush()

    @staticmethod
    def _reset_index(client: Client, index_name: str, primary_key: str) -> None:
        """Overwrite mode: drop the index and recreate it empty with the resolved
        primary key. Recreating explicitly (rather than relying on the first batch)
        keeps the index present even when the sync emits zero records, and only a
        missing index is a tolerable delete failure — anything else (auth, network,
        failed task) must abort so stale data can't silently survive an 'overwrite'.
        """
        logger.info(f"Overwrite: resetting index '{index_name}'")
        try:
            task = client.delete_index(index_name)
            result = client.wait_for_task(task.task_uid, 600_000, 500)
            if result.status != "succeeded" and (getattr(result, "error", None) or {}).get("code") != "index_not_found":
                raise RuntimeError(f"Failed to delete index '{index_name}' for overwrite: {getattr(result, 'error', None)}")
        except MeilisearchApiError as e:
            if e.code != "index_not_found":
                raise
        task = client.create_index(index_name, {"primaryKey": primary_key})
        result = client.wait_for_task(task.task_uid, 600_000, 500)
        if result.status != "succeeded":
            raise RuntimeError(f"Failed to create index '{index_name}': {getattr(result, 'error', None)}")

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        # Unique uid per run: never touches a real index and can't race a concurrent check.
        index_name = f"_airbyte_check_{uuid4().hex}"
        client = None
        try:
            client = get_client(config=config)
            doc_id = "airbyte-check-1"

            # Write
            task = client.index(index_name).add_documents([{"id": doc_id, "title": "Airbyte connection check"}], "id")
            result = client.wait_for_task(task.task_uid, 60_000, 200)
            if result.status != "succeeded":
                return AirbyteConnectionStatus(
                    status=Status.FAILED, message=f"Write check failed: task status '{result.status}'"
                )

            # Read
            client.index(index_name).get_document(doc_id)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Check connection failed. Error: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
        finally:
            if client is not None:
                try:
                    client.delete_index(index_name)
                except Exception as e:
                    logger.warning(f"Failed to delete check index '{index_name}': {e}")
