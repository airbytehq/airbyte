/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.snapshot

import com.mongodb.client.FindIterable
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Projections
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import io.airbyte.integrations.source.mongodb.discover.schemaFieldTypesOf
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbCdcState
import io.airbyte.integrations.source.mongodb.read.partition.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodb.read.partition.RecordAcceptor
import io.airbyte.integrations.source.mongodb.read.record.MongoDbRecordConverter
import io.airbyte.integrations.source.mongodb.read.record.MongoDbSharedState
import io.airbyte.protocol.models.v0.AirbyteAnalyticsTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.bson.BsonTimestamp
import org.bson.RawBsonDocument

private val log = KotlinLogging.logger {}

/**
 * Reads a collection ordered by `_id` in one query per round, resuming after the checkpointed
 * `_id`. Exhausting the collection checkpoints the terminal status (`COMPLETE` / `FULL_REFRESH`)
 * and marks the stream complete for this READ; a round cut short (checkpoint interval, WASS budget)
 * checkpoints `IN_PROGRESS` / `FULL_REFRESH` so the next one continues.
 */
class MongoDbSnapshotPartitionReader(
    sharedState: MongoDbSharedState,
    private val feedBootstrap: StreamFeedBootstrap,
) : MongoDbPartitionReaderBase(sharedState, feedBootstrap) {

    private val stream: Stream = feedBootstrap.feed
    private val isFullRefresh: Boolean =
        stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH
    private val converter =
        MongoDbRecordConverter(sharedState.configuration.schemaEnforced, schemaFieldTypesOf(stream))
    private val collection: MongoCollection<RawBsonDocument> by lazy {
        sharedState.client
            .getDatabase(stream.namespace!!)
            .getCollection(stream.name, RawBsonDocument::class.java)
    }
    /**
     * `_ab_cdc_cursor` for this snapshot: the time of the resume token the `Global` feed saved
     * before the snapshots started ([MongoDbCdcState.cdcSyncedUntil]); none without CDC.
     */
    private val snapshotCursor: BsonTimestamp? by lazy {
        feedBootstrap.feeds
            .filterIsInstance<Global>()
            .firstOrNull()
            ?.let { MongoDbCdcState.fromOpaqueStateValue(feedBootstrap.currentState(it)) }
            ?.cdcSyncedUntil
            ?.let { BsonTimestamp(it.epochSecond.toInt(), 0) }
    }

    // `checkpoint()` may run on another thread than `run()` after a timeout, hence volatile.
    @Volatile private var numRecords = 0L
    @Volatile private var lastId: Any? = null
    @Volatile private var finished = false

    override suspend fun run() {
        val emit: RecordAcceptor =
            checkNotNull(recordAcceptorFor(stream.id)) { "No record acceptor for ${stream.id}" }
        if (sharedState.logStreamStart(stream.id)) warnIfIdTypesAreMixed()
        val startId: Any? = resumeFromId()
        lastId = startId
        log.info { "Reading ${stream.namespace}.${stream.name} after _id=$startId." }

        query(startId).cursor().use { cursor ->
            while (cursor.hasNext()) {
                currentCoroutineContext().ensureActive()
                if (shouldYieldToCdc()) {
                    sharedState.snapshotYielded.add(stream.id)
                    return
                }
                val document: RawBsonDocument = cursor.next()
                val payload: NativeRecordPayload = converter.toPayload(document)
                stampCursor(payload, snapshotCursor)
                emit(payload, null)
                lastId = document[ID_FIELD]
                numRecords++
            }
        }
        finished = true
        sharedState.completedSnapshots.add(stream.id)
        log.info { "Finished ${stream.namespace}.${stream.name}: $numRecords records." }
    }

    /**
     * Ordered `_id` scan after [startId] (the sort on `_id` may spill to disk), in batches bounded
     * by the 16MB message size only; one query runs until the collection is exhausted or the round
     * is cut short. Under `schema_enforced` only the fields a record is built from are projected
     * (extra fields would be dropped anyway); schemaless needs the whole document.
     */
    private fun query(startId: Any?): FindIterable<RawBsonDocument> {
        val find: FindIterable<RawBsonDocument> = collection.find()
        startId?.let { find.filter(Filters.gt(ID_FIELD, it)) }
        if (sharedState.configuration.schemaEnforced) {
            find.projection(Projections.include(converter.readFields.toList()))
        }
        return find
            .sort(Sorts.ascending(ID_FIELD))
            .batchSize(sharedState.snapshotBatchSize)
            .allowDiskUse(true)
    }

    /**
     * WASS: an incremental snapshot yields past the deadline, but only after at least one record so
     * it always progresses. Full refresh never yields (no change stream to drain).
     */
    private fun shouldYieldToCdc(): Boolean =
        !isFullRefresh && numRecords > 0 && Instant.now().isAfter(sharedState.snapshotDeadline)

    /**
     * As the legacy connector did: a collection mixing `_id` types is not refused, but it reads the
     * checkpointed type only once resumed (see [MongoDbIdTypes]), so the sync warns and emits the
     * legacy analytics trace once per stream.
     */
    private fun warnIfIdTypesAreMixed() {
        val types: List<String> = sharedState.idTypes(stream.id)
        if (types.size <= 1) return
        log.warn {
            "The _id fields in this collection are not consistently typed, which may lead to " +
                "data loss (collection = ${stream.name}, types = $types)."
        }
        feedBootstrap.outputConsumer.accept(
            AirbyteAnalyticsTraceMessage().withType(MongoDbIdTypes.ANALYTICS_KEY).withValue("1"),
        )
    }

    /** The `_id` to resume after; null for a fresh read (no state, or already complete). */
    private fun resumeFromId(): Any? =
        MongoDbStreamStateValue.fromCurrentState(currentState())
            ?.takeUnless { it.status == MongoDbSnapshotStatus.COMPLETE }
            ?.resumeIdValue()

    /** The feed's current checkpoint; for a full refresh the READ's input until one is written. */
    private fun currentState(): OpaqueStateValue? =
        feedBootstrap.currentState
            ?: if (isFullRefresh) sharedState.fullRefreshInputState(stream.id) else null

    /**
     * Full-refresh streams never become `COMPLETE`: their snapshot is re-read every sync. A
     * finished full refresh checkpoints no `_id` so the next sync starts over, while an interrupted
     * one keeps its last `_id` so a retry resumes.
     */
    override fun checkpoint(): PartitionReadCheckpoint {
        val status: MongoDbSnapshotStatus =
            when {
                isFullRefresh -> MongoDbSnapshotStatus.FULL_REFRESH
                finished -> MongoDbSnapshotStatus.COMPLETE
                else -> MongoDbSnapshotStatus.IN_PROGRESS
            }
        val checkpointId: Any? = if (isFullRefresh && finished) null else lastId
        return PartitionReadCheckpoint(
            MongoDbStreamStateValue.fromLastId(checkpointId, status).toOpaqueStateValue(),
            numRecords,
            checkpointPartitionId,
        )
    }
}
