/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Projections
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.integrations.source.mongodb.config.MongoDbClientFactory
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfiguration
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbIdKind
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbStreamStateValue
import io.micronaut.context.annotation.Value
import jakarta.annotation.PreDestroy
import jakarta.inject.Singleton
import java.time.Duration
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import org.bson.BsonTimestamp
import org.bson.Document
import org.bson.conversions.Bson

/** State shared by a READ's creators and readers: config, one [MongoClient], CDK resources. */
@Singleton
class MongoDbSharedState(
    val configuration: MongoDbSourceConfiguration,
    private val concurrencyResource: ConcurrencyResource,
    private val resourceAcquirer: ResourceAcquirer,
    /** Test hook: records per snapshot `run()` before checkpointing (`0` = unlimited). */
    @Value("\${airbyte.connector.extract.mongodb.max-records-per-run:0}")
    val maxRecordsPerRun: Long = 0,
    /**
     * Test hook: the WASS budget in ms (`0` = `maxSnapshotReadDuration`; negative = already
     * expired, so an incremental snapshot yields after its first record).
     */
    @Value("\${airbyte.connector.extract.mongodb.max-snapshot-duration-ms:0}")
    private val maxSnapshotDurationMsOverride: Long = 0,
) {
    /** One client for the whole READ; MongoDB pools connections internally. */
    val client: MongoClient by lazy { MongoDbClientFactory.create(configuration) }

    /**
     * The oplog time of the change-stream position this READ saved (the token it captured on a cold
     * start, or checkpointed after draining): every event a later sync replays is strictly after
     * it, so snapshot rows stamped with it always lose to the changes that supersede them,
     * whichever node served the snapshot. Set by the CDC reader, which runs before the snapshots;
     * null when no stream is incremental.
     */
    @Volatile var snapshotCursorTime: BsonTimestamp? = null

    /**
     * Whether the server accepts `fullDocumentBeforeChange` (MongoDB 6.0+): a change stream opened
     * with it on an older server fails with an unrecognized-field error.
     */
    val supportsPreImages: Boolean by lazy {
        val buildInfo: Document = client.getDatabase("admin").runCommand(Document("buildInfo", 1))
        val major: Int = (buildInfo["versionArray"] as? List<*>)?.firstOrNull() as? Int ?: 0
        major >= 6
    }

    private val idKindByStream = ConcurrentHashMap<StreamIdentifier, String>()

    /**
     * The BSON kind of the collection's `_id`s ([MongoDbIdKind]). The `_id` index orders values by
     * BSON type before value, and a resume filter `_id > x` only matches `_id`s of x's type, so a
     * collection mixing types would lose every later type after a checkpoint: the smallest and
     * largest `_id` sharing a kind means every `_id` does (two index seeks), else the sync fails.
     * Numbers of any width are one kind, as they are for the comparison.
     */
    fun idKind(streamId: StreamIdentifier): String =
        idKindByStream.computeIfAbsent(streamId) { id ->
            val collection: MongoCollection<Document> =
                client.getDatabase(id.namespace!!).getCollection(id.name)
            fun endpointKind(sort: Bson): String =
                MongoDbIdKind.of(
                    collection
                        .find()
                        .projection(Projections.include(MongoDbSourceMetadataQuerier.ID_FIELD))
                        .sort(sort)
                        .limit(1)
                        .first()
                        ?.get(MongoDbSourceMetadataQuerier.ID_FIELD)
                )
            val first: String = endpointKind(Sorts.ascending(MongoDbSourceMetadataQuerier.ID_FIELD))
            val last: String = endpointKind(Sorts.descending(MongoDbSourceMetadataQuerier.ID_FIELD))
            if (first != last) {
                throw ConfigErrorException(
                    "Collection ${id.namespace}.${id.name} has _id values of more than one type " +
                        "($first and $last). The _id type must be the same for every document " +
                        "in a collection; make it consistent or exclude the collection from the sync.",
                )
            }
            first
        }

    /**
     * Whether a snapshot of the collection can be checkpointed mid-way and resumed with `_id >
     * last`: not for an `_id` kind the checkpoint cannot encode natively (it is saved as text and
     * could not be compared). Those are read in a single round instead.
     */
    fun isResumable(streamId: StreamIdentifier): Boolean = idKind(streamId) in RESUMABLE_ID_KINDS

    /** Snapshot streams that finished in this READ, so the factory stops re-planning them. */
    val completedSnapshots: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /** Incremental snapshots that hit the WASS budget and yielded so the next sync drains CDC. */
    val snapshotYielded: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /** When an incremental snapshot yields to CDC (WASS); fixed on first access for the READ. */
    val snapshotDeadline: Instant by lazy {
        val budget: Duration =
            if (maxSnapshotDurationMsOverride != 0L)
                Duration.ofMillis(maxSnapshotDurationMsOverride)
            else checkNotNull(configuration.maxSnapshotReadDuration)
        Instant.now().plus(budget)
    }

    fun tryAcquireResourcesForCreator(): AutoCloseable? = concurrencyResource.tryAcquire()

    fun tryAcquireResourcesForReader(
        resourceTypes: List<ResourceType>,
    ): Map<ResourceType, Resource.Acquired>? = resourceAcquirer.tryAcquire(resourceTypes)

    @PreDestroy
    fun close() {
        client.close()
    }

    companion object {
        /** The kinds [MongoDbStreamStateValue] encodes natively (see [MongoDbIdKind]). */
        val RESUMABLE_ID_KINDS: Set<String> =
            setOf("number", "string", "object", "binData", "objectId", "date", "timestamp")
    }
}
