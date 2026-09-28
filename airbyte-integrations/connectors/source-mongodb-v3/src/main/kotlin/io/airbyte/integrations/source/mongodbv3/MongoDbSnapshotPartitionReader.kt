/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamRecordConsumer
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.bson.Document

private val log = KotlinLogging.logger {}

/**
 * Reads a collection ordered by `_id` ascending and emits every document as a record.
 *
 * Resumable: it starts after the `_id` recorded in the feed's current state (`_id > lastSeen`), and
 * checkpoints the last `_id` it read. If it reads the collection to the end it checkpoints the
 * terminal status (`COMPLETE` for an incremental snapshot, `FULL_REFRESH` for a full refresh) and
 * marks the stream complete for this READ; otherwise (cut short by the `checkpointTargetInterval`
 * timeout or the `max-records-per-run` test hook) it checkpoints `IN_PROGRESS`/`FULL_REFRESH` so
 * the next round continues. Splitting a collection into concurrent `_id` ranges is a later
 * optimization.
 */
class MongoDbSnapshotPartitionReader(
    private val streamState: MongoDbStreamState,
) : PartitionReader {

    private val sharedState: MongoDbSharedState = streamState.sharedState
    private val stream: Stream = streamState.stream
    private val converter = MongoDbRecordConverter(sharedState.configuration.schemaEnforced)

    private val numRecords = AtomicLong(0L)
    private val lastId = AtomicReference<Any?>(null)
    private val finished = AtomicBoolean(false)

    private val acquiredResources = AtomicReference<Map<ResourceType, ReaderAcquiredResource>>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resources: Map<ResourceType, ReaderAcquiredResource> =
            sharedState.tryAcquireResourcesForReader(listOf(ResourceType.RESOURCE_DB_CONNECTION))
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        val recordConsumer: StreamRecordConsumer =
            streamState.streamFeedBootstrap.streamRecordConsumers()[stream.id]
                ?: throw IllegalStateException("No record consumer for stream ${stream.id}")
        val startId: Any? = resumeFromId()
        lastId.set(startId)
        val collection: MongoCollection<Document> =
            sharedState.client.getDatabase(stream.namespace!!).getCollection(stream.name)
        var find = collection.find()
        if (startId != null) {
            find = find.filter(Filters.gt(MongoDbSourceMetadataQuerier.ID_FIELD, startId))
        }
        val maxRecords: Long = sharedState.maxRecordsPerRun
        log.info {
            "Reading ${stream.namespace}.${stream.name} ordered by _id" +
                (startId?.let { " resuming after $it" } ?: "") +
                "."
        }
        find.sort(Sorts.ascending(MongoDbSourceMetadataQuerier.ID_FIELD)).cursor().use { cursor ->
            while (cursor.hasNext()) {
                currentCoroutineContext().ensureActive()
                if (maxRecords in 1..numRecords.get()) {
                    log.info { "Reached max-records-per-run ($maxRecords); checkpointing." }
                    return
                }
                if (shouldYieldToCdc()) {
                    sharedState.snapshotYielded.add(stream.id)
                    log.info { "WASS snapshot budget reached for ${stream.id}; yielding to CDC." }
                    return
                }
                val document: Document = cursor.next()
                val (payload: NativeRecordPayload, rawId: Any?) =
                    converter.toPayloadWithId(document)
                recordConsumer.accept(payload, null)
                lastId.set(rawId)
                numRecords.incrementAndGet()
            }
            finished.set(true)
            sharedState.completedSnapshots.add(stream.id)
        }
        log.info { "Finished ${stream.namespace}.${stream.name}: ${numRecords.get()} records." }
    }

    /**
     * WASS: an incremental snapshot yields once past the shared snapshot deadline, but only after
     * emitting at least one record so it always makes forward progress. Full-refresh streams never
     * yield (there is no change stream to drain, and the destination expects the whole snapshot).
     */
    private fun shouldYieldToCdc(): Boolean =
        !streamState.isFullRefresh &&
            numRecords.get() > 0 &&
            java.time.Instant.now().isAfter(sharedState.snapshotDeadline())

    /**
     * The `_id` to resume after, or null for a fresh read (no state, or an already-complete one).
     */
    private fun resumeFromId(): Any? {
        val state = streamState.streamFeedBootstrap.currentState ?: return null
        return try {
            val value = MongoDbStreamStateValue.fromOpaqueStateValue(state)
            if (value.status == MongoDbSnapshotStatus.COMPLETE) null else value.resumeIdValue()
        } catch (e: Exception) {
            log.warn(e) { "Ignoring unparseable state for ${stream.id}." }
            null
        }
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        val status: MongoDbSnapshotStatus =
            if (finished.get()) {
                streamState.terminalStatus
            } else if (streamState.isFullRefresh) {
                MongoDbSnapshotStatus.FULL_REFRESH
            } else {
                MongoDbSnapshotStatus.IN_PROGRESS
            }
        return PartitionReadCheckpoint(
            MongoDbStreamStateValue.fromLastId(lastId.get(), status).toOpaqueStateValue(),
            numRecords.get(),
        )
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
    }
}
