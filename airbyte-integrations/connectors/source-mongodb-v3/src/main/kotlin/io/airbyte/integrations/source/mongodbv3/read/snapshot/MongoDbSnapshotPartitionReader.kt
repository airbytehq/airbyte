/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.snapshot

import com.mongodb.client.FindIterable
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Projections
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.Stream
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import io.airbyte.integrations.source.mongodbv3.read.partition.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodbv3.read.partition.RecordAcceptor
import io.airbyte.integrations.source.mongodbv3.read.record.MongoDbRecordConverter
import io.airbyte.integrations.source.mongodbv3.read.record.schemaFieldTypesOf
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.bson.Document
import org.bson.conversions.Bson

private val log = KotlinLogging.logger {}

/**
 * Reads a collection ordered by `_id`, resuming after the checkpointed `_id`. Reaching the end
 * checkpoints the terminal status (`COMPLETE` / `FULL_REFRESH`) and marks the stream complete for
 * this READ; being cut short (timeout, WASS budget, `max-records-per-run`) checkpoints
 * `IN_PROGRESS` / `FULL_REFRESH` so the next round continues.
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
     * Ordered `_id` scan after [startId]. Under `schema_enforced` only the catalog's fields are
     * projected (extra fields would be dropped anyway); schemaless needs the whole document.
     */
    private fun query(startId: Any?): FindIterable<Document> {
        val collection =
            sharedState.client.getDatabase(stream.namespace!!).getCollection(stream.name)
        val find: FindIterable<Document> = collection.find()
        startId?.let { find.filter(resumeFilter(it)) }
        if (sharedState.configuration.schemaEnforced) {
            find.projection(Projections.include(schemaFieldTypesOf(stream).keys.toList()))
        }
        return find.sort(Sorts.ascending(ID_FIELD))
    }

    /**
     * `$expr` compares across BSON types in sort order, so the resume continues into the next `_id`
     * type where a type-bracketed `$gt` would stop; the `_id` index is still used (bounds
     * `(startId, MaxKey]`).
     */
    private fun resumeFilter(startId: Any): Bson =
        Filters.expr(Document("\$gt", listOf("\$$ID_FIELD", Document("\$literal", startId))))

    /** Test hook: stop after `max-records-per-run` records so resume can be exercised quickly. */
    private fun reachedRecordLimit(): Boolean = sharedState.maxRecordsPerRun in 1..numRecords

    /**
     * WASS: an incremental snapshot yields past the deadline, but only after at least one record so
     * it always progresses. Full refresh never yields (no change stream to drain).
     */
    private fun shouldYieldToCdc(): Boolean =
        !streamState.isFullRefresh &&
            numRecords > 0 &&
            Instant.now().isAfter(sharedState.snapshotDeadline)

    /** The `_id` to resume after; null for a fresh read (no usable state, or already complete). */
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
