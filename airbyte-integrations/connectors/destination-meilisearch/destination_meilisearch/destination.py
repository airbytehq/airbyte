#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from logging import Logger, getLogger
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from meilisearch import Client

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
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


class DestinationMeilisearch(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        client = get_client(config=config)
        batch_size = int(config.get("batch_size") or DEFAULT_BATCH_SIZE)
        merge = config.get("update_method") == "merge"

        # Build one writer per configured stream and reset overwrite indexes up front.
        writers: Dict[str, MeiliWriter] = {}
        for stream in configured_catalog.streams:
            index_name = sanitize_index_name(stream.stream.name)
            primary_key, id_mode, key_paths = resolve_primary_key(stream)

            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                logger.info(f"Overwrite: deleting index '{index_name}'")
                try:
                    task = client.delete_index(index_name)
                    client.wait_for_task(task.task_uid)
                except Exception as e:
                    logger.info(f"Could not delete index '{index_name}' (it may not exist): {e}")

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
                # Flush before checkpointing so acknowledged state reflects persisted data.
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

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        index_name = "_airbyte_check"
        try:
            client = get_client(config=config)
            doc_id = "airbyte-check-1"

            # Write
            task = client.index(index_name).add_documents([{"id": doc_id, "title": "Airbyte connection check"}], "id")
            result = client.wait_for_task(task.task_uid, 60_000, 500)
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
            try:
                get_client(config=config).delete_index(index_name)
            except Exception:
                logger.warning(f"Failed to delete check index '{index_name}'")
