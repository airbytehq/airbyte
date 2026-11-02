#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
import time
import uuid
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    FailureType,
    Status,
    TraceType,
    Type,
)
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from destination_meilisearch.client import MeiliClient
from destination_meilisearch.writer import GENERATION_ID, PRIMARY_KEY, StreamWriter, index_uid


logger = logging.getLogger("airbyte")

DEFAULT_BATCH_SIZE = 10000
# Pending tasks are also waited for once this many have accumulated, which
# bounds how far the destination can get ahead of Meilisearch, and how late a
# failed task is noticed.
MAX_PENDING_TASKS = 100
# State messages are held back while records keep arriving, so that sources
# which emit state often don't cause a request and a wait for every few
# records. They are emitted once a batch of records has arrived since the last
# checkpoint, or once they have been held for this long.
CHECKPOINT_INTERVAL_SECONDS = 30.0

# The connection check fails fast rather than retrying for minutes.
CHECK_TIMEOUT_SECONDS = 10
CHECK_MAX_ATTEMPTS = 2

StreamKey = Tuple[Optional[str], str]


def get_client(config: Mapping[str, Any]) -> MeiliClient:
    return MeiliClient(config["host"], config.get("api_key"))


def stream_index(configured_stream: ConfiguredAirbyteStream) -> str:
    stream = configured_stream.stream
    if configured_stream.destination_object_name:
        return index_uid(configured_stream.destination_object_name)
    return index_uid(stream.name, stream.namespace)


def truncation_generation(configured_stream: ConfiguredAirbyteStream) -> Optional[int]:
    """Returns the generation below which documents of a stream are deleted once
    the stream completes, or None if documents are kept.

    Overwrites delete the documents of every earlier generation, and refreshes
    which truncate the stream delete those below its minimum generation.
    """
    generation = configured_stream.generation_id
    if generation is None:
        return None
    minimum = configured_stream.minimum_generation_id or 0
    if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
        return max(minimum, generation)
    return minimum if minimum > 0 else None


def check_unique_indexes(configured_catalog: ConfiguredAirbyteCatalog) -> None:
    """Raises an error if two streams would be written to the same index, since
    one could then delete the documents of the other."""
    seen: Dict[str, str] = {}
    for configured_stream in configured_catalog.streams:
        stream = configured_stream.stream
        name = f"{stream.namespace}.{stream.name}" if stream.namespace else stream.name
        uid = stream_index(configured_stream)
        if uid in seen:
            raise AirbyteTracedException(
                message=f"Streams '{seen[uid]}' and '{name}' would both be written to the index '{uid}'. Rename one of them, or sync them in different connections.",
                failure_type=FailureType.config_error,
            )
        seen[uid] = name


class DestinationMeilisearch(Destination):
    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        client = get_client(config)
        batch_size = config.get("batch_size") or DEFAULT_BATCH_SIZE

        check_unique_indexes(configured_catalog)
        streams: Dict[StreamKey, ConfiguredAirbyteStream] = {}
        writers: Dict[StreamKey, StreamWriter] = {}
        for configured_stream in configured_catalog.streams:
            key = (configured_stream.stream.namespace, configured_stream.stream.name)
            streams[key] = configured_stream
            writers[key] = self._prepare_stream(client, configured_stream, batch_size)

        held_states: List[AirbyteMessage] = []
        records_since_checkpoint = 0
        last_checkpoint = time.monotonic()

        def checkpoint() -> Iterable[AirbyteMessage]:
            """Sends all buffered records, waits for Meilisearch to apply them,
            and then emits the held state messages."""
            nonlocal records_since_checkpoint, last_checkpoint
            for writer in writers.values():
                writer.flush()
            pending = [uid for writer in writers.values() for uid in writer.pending_tasks]
            client.wait_for_tasks(pending)
            for writer in writers.values():
                writer.pending_tasks.clear()
            records_since_checkpoint = 0
            last_checkpoint = time.monotonic()
            yield from held_states
            held_states.clear()

        completed = set()
        for message in input_messages:
            if message.type == Type.RECORD:
                record = message.record
                writer = writers.get((record.namespace, record.stream))
                if writer is None:
                    logger.debug(f"Stream {record.stream} is not in the configured catalog, skipping its record")
                    continue
                try:
                    writer.write(record.data)
                except ValueError as err:
                    raise AirbyteTracedException(
                        message=f"Stream '{record.stream}' has a record which can't be written: {err}",
                        failure_type=FailureType.config_error,
                    ) from err
                records_since_checkpoint += 1
                if len(writer.pending_tasks) >= MAX_PENDING_TASKS:
                    yield from checkpoint()
            elif message.type == Type.STATE:
                # A state message may only be emitted once every record before
                # it has been applied.
                held_states.append(message)
                if (
                    records_since_checkpoint == 0
                    or records_since_checkpoint >= batch_size
                    or time.monotonic() - last_checkpoint >= CHECKPOINT_INTERVAL_SECONDS
                ):
                    yield from checkpoint()
            elif message.type == Type.TRACE and message.trace.type == TraceType.STREAM_STATUS:
                status = message.trace.stream_status
                if status.status == AirbyteStreamStatus.COMPLETE:
                    descriptor = status.stream_descriptor
                    completed.add((descriptor.namespace, descriptor.name))

        yield from checkpoint()

        for key, configured_stream in streams.items():
            generation = truncation_generation(configured_stream)
            if generation is not None:
                self._delete_earlier_generations(client, configured_stream, generation, completed_stream=key in completed)
            writer = writers[key]
            logger.info(
                f"Stream '{configured_stream.stream.name}': wrote {writer.records_written} and deleted {writer.records_deleted} documents in index '{writer.index}'"
            )

    def _prepare_stream(self, client: MeiliClient, configured_stream: ConfiguredAirbyteStream, batch_size: int) -> StreamWriter:
        uid = stream_index(configured_stream)
        client.ensure_index(uid, PRIMARY_KEY)

        if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite and configured_stream.generation_id is None:
            # Without generations, there is no way to tell the documents of
            # this sync apart from earlier ones, so an overwrite can only delete
            # the existing documents up front.
            logger.info(f"Deleting all documents from index '{uid}' before overwriting it")
            client.run(f"delete all documents from index '{uid}'", client.client.index(uid).delete_all_documents)

        primary_key = None
        if configured_stream.destination_sync_mode == DestinationSyncMode.append_dedup:
            primary_key = configured_stream.primary_key or configured_stream.stream.source_defined_primary_key
            if not primary_key:
                raise AirbyteTracedException(
                    message=f"Stream '{configured_stream.stream.name}' uses deduplication but has no primary key",
                    failure_type=FailureType.config_error,
                )

        return StreamWriter(client, uid, batch_size, primary_key=primary_key, generation_id=configured_stream.generation_id)

    def _delete_earlier_generations(
        self, client: MeiliClient, configured_stream: ConfiguredAirbyteStream, generation: int, completed_stream: bool
    ) -> None:
        uid = stream_index(configured_stream)
        if not completed_stream:
            # Deleting the earlier documents of a stream that didn't finish
            # would leave the index with only part of its data. They are
            # deleted by the sync which completes the stream instead.
            logger.warning(
                f"Stream '{configured_stream.stream.name}' was not reported as complete, so documents of earlier generations in index '{uid}' are kept"
            )
            return

        # Making the attribute filterable re-indexes the documents, so it is
        # done once the data has been written, and only when it is needed.
        client.ensure_filterable(uid, GENERATION_ID)

        logger.info(f"Deleting documents of generations before {generation} from index '{uid}'")
        doc_filter = f"{GENERATION_ID} < {generation} OR {GENERATION_ID} NOT EXISTS"
        client.run(
            f"delete earlier generations from index '{uid}'",
            lambda: client.client.index(uid).delete_documents(filter=doc_filter),
        )

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        client = MeiliClient(config["host"], config.get("api_key"), timeout=CHECK_TIMEOUT_SECONDS, max_attempts=CHECK_MAX_ATTEMPTS)
        uid = f"_airbyte_check_{uuid.uuid4().hex}"
        created = False
        try:
            version = client.client.get_version()
            logger.info(f"Connected to Meilisearch {version.get('pkgVersion')}")

            # Check that the API key can create indexes and write documents.
            client.ensure_index(uid, PRIMARY_KEY)
            created = True
            client.run(
                f"add a document to index '{uid}'",
                lambda: client.client.index(uid).add_documents([{PRIMARY_KEY: "check"}], primary_key=PRIMARY_KEY),
            )
            status = AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            status = AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {e}")

        if created:
            try:
                client.run(f"delete index '{uid}'", lambda: client.client.delete_index(uid))
            except Exception as e:
                logger.warning(f"Failed to delete index '{uid}' created by the connection check: {e}")
        return status
