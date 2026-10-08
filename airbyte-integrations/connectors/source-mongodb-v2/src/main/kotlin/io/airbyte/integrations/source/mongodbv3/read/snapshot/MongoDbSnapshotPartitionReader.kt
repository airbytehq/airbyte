/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.snapshot

import com.mongodb.client.FindIterable
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Projections
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbFieldType
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import io.airbyte.integrations.source.mongodbv3.discover.schemaFieldTypesOf
import io.airbyte.integrations.source.mongodbv3.read.partition.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodbv3.read.partition.RecordAcceptor
import io.airbyte.integrations.source.mongodbv3.read.record.MongoDbRecordConverter
import io.airbyte.integrations.source.mongodbv3.read.record.MongoDbSharedState
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

    // `checkpoint()` may run on another thread than `run()` after a timeout, hence volatile.
    @Volatile private var numRecords = 0L
    @Volatile private var lastId: Any? = null
    @Volatile private var finished = false

    override suspend fun run() {
        val emit: RecordAcceptor =
            checkNotNull(recordAcceptorFor(stream.id)) { "No record acceptor for ${stream.id}" }
        requireSingleIdType()
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
        val find: FindIterable<Document> = collection.find()
        startId?.let { find.filter(Filters.gt(ID_FIELD, it)) }
        if (sharedState.configuration.schemaEnforced) {
            find.projection(Projections.include(schemaFieldTypes.keys.toList()))
        }
        return find.sort(Sorts.ascending(ID_FIELD))
    }

    /**
     * The `_id` index orders values by BSON type before value, and the resume filter `_id > x` only
     * matches `_id`s of x's type: a collection mixing types would lose every later type after a
     * checkpoint. The smallest and largest `_id` sharing a type means every `_id` does (two index
     * seeks). Numbers of any width are one type, as they are for the comparison.
     */
    private fun requireSingleIdType() {
        fun endpointIdType(sort: Bson): String =
            MongoDbIdKind.of(
                collection
                    .find()
                    .projection(Projections.include(ID_FIELD))
                    .sort(sort)
                    .limit(1)
                    .first()
                    ?.get(ID_FIELD)
            )
        val first: String = endpointIdType(Sorts.ascending(ID_FIELD))
        val last: String = endpointIdType(Sorts.descending(ID_FIELD))
        if (first != last) {
            throw ConfigErrorException(
                "Collection ${stream.namespace}.${stream.name} has _id values of more than one " +
                    "type ($first and $last). The _id type must be the same for every document " +
                    "in a collection; make it consistent or exclude the collection from the sync.",
            )
        }
    }

    /** Test hook: stop after `max-records-per-run` records so resume can be exercised quickly. */
    private fun reachedRecordLimit(): Boolean = sharedState.maxRecordsPerRun in 1..numRecords

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
        )
    }
}
