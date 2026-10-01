/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.snapshot

import com.mongodb.client.FindIterable
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Projections
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.Stream
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import io.airbyte.integrations.source.mongodbv3.read.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodbv3.read.MongoDbRecordConverter
import io.airbyte.integrations.source.mongodbv3.read.RecordAcceptor
import io.airbyte.integrations.source.mongodbv3.read.schemaFieldTypesOf
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
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
 * timeout, the WASS budget, or the `max-records-per-run` test hook) it checkpoints
 * `IN_PROGRESS`/`FULL_REFRESH` so the next round continues. Splitting a collection into concurrent
 * `_id` ranges is a later optimization.
 */
class MongoDbSnapshotPartitionReader(
    private val streamState: MongoDbStreamState,
) : MongoDbPartitionReaderBase(streamState.sharedState, streamState.streamFeedBootstrap) {

    private val stream: Stream = streamState.stream
    private val converter =
        MongoDbRecordConverter(sharedState.configuration.schemaEnforced, schemaFieldTypesOf(stream))

    // `checkpoint()` may run on another thread than `run()` after a timeout, hence volatile.
    @Volatile private var numRecords = 0L
    @Volatile private var lastId: Any? = null
    @Volatile private var finished = false

    override suspend fun run() {
        val emit: RecordAcceptor =
            checkNotNull(recordAcceptorFor(stream.id)) { "No record acceptor for ${stream.id}" }
        val startId: Any? = resumeFromId()
        lastId = startId
        log.info { "Reading ${stream.namespace}.${stream.name} after _id=$startId." }

        query(startId).cursor().use { cursor ->
            while (cursor.hasNext()) {
                currentCoroutineContext().ensureActive()
                if (reachedRecordLimit()) return
                if (shouldYieldToCdc()) {
                    sharedState.snapshotYielded.add(stream.id)
                    return
                }
                val (payload, rawId) = converter.toPayloadWithId(cursor.next())
                emit(payload, null)
                lastId = rawId
                numRecords++
            }
        }
        finished = true
        sharedState.completedSnapshots.add(stream.id)
        log.info { "Finished ${stream.namespace}.${stream.name}: $numRecords records." }
    }

    /**
     * Ordered `_id` scan resuming after [startId]. Under `schema_enforced` only the catalog's
     * fields are projected so documents' extra fields never cross the wire (the record consumer
     * would drop them anyway); schemaless mode needs the whole document for its `data` field.
     */
    private fun query(startId: Any?): FindIterable<Document> {
        val collection =
            sharedState.client.getDatabase(stream.namespace!!).getCollection(stream.name)
        val find: FindIterable<Document> = collection.find()
        startId?.let { find.filter(Filters.gt(ID_FIELD, it)) }
        if (sharedState.configuration.schemaEnforced) {
            find.projection(Projections.include(schemaFieldTypesOf(stream).keys.toList()))
        }
        return find.sort(Sorts.ascending(ID_FIELD))
    }

    /** Test hook: stop after `max-records-per-run` records so resume can be exercised quickly. */
    private fun reachedRecordLimit(): Boolean = sharedState.maxRecordsPerRun in 1..numRecords

    /**
     * WASS: an incremental snapshot yields once past the shared snapshot deadline, but only after
     * emitting at least one record so it always makes forward progress. Full-refresh streams never
     * yield (there is no change stream to drain, and the destination expects the whole snapshot).
     */
    private fun shouldYieldToCdc(): Boolean =
        !streamState.isFullRefresh &&
            numRecords > 0 &&
            Instant.now().isAfter(sharedState.snapshotDeadline)

    /**
     * The `_id` to resume after, or null for a fresh read (no usable state, or one already
     * complete).
     */
    private fun resumeFromId(): Any? =
        MongoDbStreamStateValue.fromOpaqueStateValueOrNull(
                streamState.streamFeedBootstrap.currentState
            )
            ?.takeUnless { it.status == MongoDbSnapshotStatus.COMPLETE }
            ?.resumeIdValue()

    override fun checkpoint(): PartitionReadCheckpoint {
        val status: MongoDbSnapshotStatus =
            when {
                finished -> streamState.terminalStatus
                streamState.isFullRefresh -> MongoDbSnapshotStatus.FULL_REFRESH
                else -> MongoDbSnapshotStatus.IN_PROGRESS
            }
        return PartitionReadCheckpoint(
            MongoDbStreamStateValue.fromLastId(lastId, status).toOpaqueStateValue(),
            numRecords,
        )
    }
}
