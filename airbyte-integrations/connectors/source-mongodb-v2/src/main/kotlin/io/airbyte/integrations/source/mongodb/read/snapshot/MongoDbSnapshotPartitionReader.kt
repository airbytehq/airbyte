/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.snapshot

import com.mongodb.client.FindIterable
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Projections
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.mongodb.discover.MongoDbFieldType
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import io.airbyte.integrations.source.mongodb.discover.schemaFieldTypesOf
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbCdcState
import io.airbyte.integrations.source.mongodb.read.partition.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodb.read.partition.RecordAcceptor
import io.airbyte.integrations.source.mongodb.read.record.MongoDbRecordConverter
import io.airbyte.integrations.source.mongodb.read.record.MongoDbSharedState
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.bson.BsonTimestamp
import org.bson.Document

private val log = KotlinLogging.logger {}

/**
 * Reads a collection ordered by `_id`, one chunk of [MongoDbSharedState.chunkSize] documents per
 * round, resuming after the checkpointed `_id`. A short chunk is the end: it checkpoints the
 * terminal status (`COMPLETE` / `FULL_REFRESH`) and marks the stream complete for this READ; a full
 * chunk, or being cut short (timeout, WASS budget), checkpoints `IN_PROGRESS` / `FULL_REFRESH` so
 * the next round continues.
 */
class MongoDbSnapshotPartitionReader(
    sharedState: MongoDbSharedState,
    private val feedBootstrap: StreamFeedBootstrap,
) : MongoDbPartitionReaderBase(sharedState, feedBootstrap) {

    private val stream: Stream = feedBootstrap.feed
    private val isFullRefresh: Boolean =
        stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH
    private val schemaFieldTypes: Map<String, MongoDbFieldType> = schemaFieldTypesOf(stream)
    private val converter =
        MongoDbRecordConverter(sharedState.configuration.schemaEnforced, schemaFieldTypes)
    private val collection: MongoCollection<Document> by lazy {
        sharedState.client.getDatabase(stream.namespace!!).getCollection(stream.name)
    }
    /**
     * `_ab_cdc_cursor` for this snapshot: the time of the resume token the `Global` feed saved
     * before the snapshots started ([MongoDbCdcState.snapshotCursorTime]); none without CDC.
     */
    private val snapshotCursor: BsonTimestamp? by lazy {
        feedBootstrap.feeds
            .filterIsInstance<Global>()
            .firstOrNull()
            ?.let { MongoDbCdcState.fromOpaqueStateValue(feedBootstrap.currentState(it)) }
            ?.snapshotCursorTime
            ?.let { BsonTimestamp(it.epochSecond.toInt(), 0) }
    }

    // `checkpoint()` may run on another thread than `run()` after a timeout, hence volatile.
    @Volatile private var numRecords = 0L
    @Volatile private var lastId: Any? = null
    @Volatile private var finished = false

    override suspend fun run() {
        val emit: RecordAcceptor =
            checkNotNull(recordAcceptorFor(stream.id)) { "No record acceptor for ${stream.id}" }
        sharedState.checkUniformIdKind(stream.id)
        val startId: Any? = resumeFromId()
        lastId = startId
        val chunkSize: Int = sharedState.chunkSize(stream.id)
        log.info {
            "Reading ${stream.namespace}.${stream.name} after _id=$startId, up to $chunkSize documents."
        }

        query(startId, chunkSize).cursor().use { cursor ->
            while (cursor.hasNext()) {
                currentCoroutineContext().ensureActive()
                if (shouldYieldToCdc()) {
                    sharedState.snapshotYielded.add(stream.id)
                    return
                }
                val (payload, rawId) = converter.toPayloadWithId(cursor.next())
                stampCursor(payload, snapshotCursor)
                emit(payload, null)
                lastId = rawId
                numRecords++
            }
        }
        if (numRecords < chunkSize) {
            finished = true
            sharedState.completedSnapshots.add(stream.id)
            log.info { "Finished ${stream.namespace}.${stream.name}: $numRecords records." }
        } else {
            log.info {
                "Read a full chunk of ${stream.namespace}.${stream.name}; $numRecords records. " +
                    "the next round continues after _id=$lastId."
            }
        }
    }

    /**
     * Ordered `_id` scan of one chunk after [startId], as the legacy connector queried (sort on
     * `_id` may spill to disk). Under `schema_enforced` only the catalog's fields are projected
     * (extra fields would be dropped anyway); schemaless needs the whole document.
     */
    private fun query(startId: Any?, chunkSize: Int): FindIterable<Document> {
        val find: FindIterable<Document> = collection.find()
        startId?.let { find.filter(Filters.gt(ID_FIELD, it)) }
        if (sharedState.configuration.schemaEnforced) {
            find.projection(Projections.include(schemaFieldTypes.keys.toList()))
        }
        return find.sort(Sorts.ascending(ID_FIELD)).limit(chunkSize).allowDiskUse(true)
    }

    /**
     * WASS: an incremental snapshot yields past the deadline, but only after at least one record so
     * it always progresses. Full refresh never yields (no change stream to drain).
     */
    private fun shouldYieldToCdc(): Boolean =
        !isFullRefresh && numRecords > 0 && Instant.now().isAfter(sharedState.snapshotDeadline)

    /** The `_id` to resume after; null for a fresh read (no state, or already complete). */
    private fun resumeFromId(): Any? =
        MongoDbStreamStateValue.fromCurrentState(feedBootstrap.currentState)
            ?.takeUnless { it.status == MongoDbSnapshotStatus.COMPLETE }
            ?.resumeIdValue()

    /** Full-refresh streams never become `COMPLETE`: their snapshot is re-read every sync. */
    override fun checkpoint(): PartitionReadCheckpoint {
        val status: MongoDbSnapshotStatus =
            when {
                isFullRefresh -> MongoDbSnapshotStatus.FULL_REFRESH
                finished -> MongoDbSnapshotStatus.COMPLETE
                else -> MongoDbSnapshotStatus.IN_PROGRESS
            }
        return PartitionReadCheckpoint(
            MongoDbStreamStateValue.fromLastId(lastId, status).toOpaqueStateValue(),
            numRecords,
            checkpointPartitionId,
        )
    }
}
