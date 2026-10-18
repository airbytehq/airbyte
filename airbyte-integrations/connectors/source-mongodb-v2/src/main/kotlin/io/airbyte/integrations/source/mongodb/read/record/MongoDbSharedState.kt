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
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.annotation.PreDestroy
import jakarta.inject.Singleton
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import org.bson.Document
import org.bson.conversions.Bson

private val log = KotlinLogging.logger {}

/** State shared by a READ's creators and readers: config, one [MongoClient], CDK resources. */
@Singleton
class MongoDbSharedState(
    val configuration: MongoDbSourceConfiguration,
    private val concurrencyResource: ConcurrencyResource,
    private val resourceAcquirer: ResourceAcquirer,
    /** Test hook: caps [chunkSize] so a resume can be exercised on a few documents (`0` = off). */
    @Value("\${airbyte.connector.extract.mongodb.max-records-per-run:0}")
    private val maxRecordsPerRun: Long = 0,
) {
    /** One client for the whole READ; MongoDB pools connections internally. */
    val client: MongoClient by lazy { MongoDbClientFactory.create(configuration) }

    /**
     * Whether the server accepts `fullDocumentBeforeChange` (MongoDB 6.0+): a change stream opened
     * with it on an older server fails with an unrecognized-field error.
     */
    val supportsPreImages: Boolean by lazy {
        val buildInfo: Document = client.getDatabase("admin").runCommand(Document("buildInfo", 1))
        val major: Int = (buildInfo["versionArray"] as? List<*>)?.firstOrNull() as? Int ?: 0
        major >= 6
    }

    private val chunkSizeByStream = ConcurrentHashMap<StreamIdentifier, Int>()

    /**
     * Documents per snapshot query, sized as the legacy connector did: about [QUERY_TARGET_BYTES]
     * worth, from `$collStats` (`storageStats.size / count`, summed over the shards a `mongos`
     * reports), [DEFAULT_CHUNK_SIZE] when the stats are unavailable or degenerate. Each round is
     * one `find().sort(_id).limit(chunk)`, so no cursor outlives about a gigabyte of results and
     * every chunk ends with a checkpoint.
     */
    fun chunkSize(streamId: StreamIdentifier): Int =
        chunkSizeByStream.computeIfAbsent(streamId) { id ->
            val chunk: Int = chunkSizeFromStats(id)
            if (maxRecordsPerRun in 1 until chunk.toLong()) maxRecordsPerRun.toInt() else chunk
        }

    private fun chunkSizeFromStats(id: StreamIdentifier): Int {
        val name = "${id.namespace}.${id.name}"
        try {
            var count = 0L
            var size = 0L
            client
                .getDatabase(id.namespace!!)
                .getCollection(id.name)
                .aggregate(listOf(Document("\$collStats", Document("storageStats", Document()))))
                .forEach { stats: Document ->
                    val storage: Document =
                        stats.get("storageStats", Document::class.java) ?: return@forEach
                    count += (storage["count"] as? Number)?.toLong() ?: 0L
                    size += (storage["size"] as? Number)?.toLong() ?: 0L
                }
            val bytesPerDocument: Long = if (count > 0) size / count else 0L
            val chunk: Long =
                if (bytesPerDocument > 0) QUERY_TARGET_BYTES / bytesPerDocument else 0L
            if (chunk in 1..Int.MAX_VALUE.toLong()) {
                log.info {
                    "Snapshot chunk size for $name: $chunk documents (~$bytesPerDocument bytes each)."
                }
                return chunk.toInt()
            }
            log.info {
                "Snapshot chunk size for $name could not be determined; using $DEFAULT_CHUNK_SIZE."
            }
        } catch (e: Exception) {
            log.warn(e) {
                "Could not read the statistics of $name; using a chunk of $DEFAULT_CHUNK_SIZE."
            }
        }
        return DEFAULT_CHUNK_SIZE
    }

    private val uniformIdKindStreams: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /**
     * Fails the sync when the collection mixes `_id` kinds ([MongoDbIdKind]). The `_id` index
     * orders values by BSON type before value, and a resume filter `_id > x` only matches `_id`s of
     * x's type, so a collection mixing types would lose every later type after a checkpoint: the
     * smallest and largest `_id` sharing a kind means every `_id` does (two index seeks). Numbers
     * of any width are one kind, as they are for the comparison. Checked once per stream per READ.
     */
    fun checkUniformIdKind(streamId: StreamIdentifier) {
        if (streamId in uniformIdKindStreams) return
        val collection: MongoCollection<Document> =
            client.getDatabase(streamId.namespace!!).getCollection(streamId.name)
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
                "Collection ${streamId.namespace}.${streamId.name} has _id values of more than " +
                    "one type ($first and $last). The _id type must be the same for every " +
                    "document in a collection; make it consistent or exclude the collection " +
                    "from the sync.",
            )
        }
        uniformIdKindStreams.add(streamId)
    }

    /** Snapshot streams that finished in this READ, so the factory stops re-planning them. */
    val completedSnapshots: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /** Incremental snapshots that hit the WASS budget and yielded so the next sync drains CDC. */
    val snapshotYielded: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /** When an incremental snapshot yields to CDC (WASS); fixed on first access for the READ. */
    val snapshotDeadline: Instant by lazy {
        Instant.now().plus(checkNotNull(configuration.maxSnapshotReadDuration))
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
        /** Documents per snapshot query when the collection's statistics give no better figure. */
        const val DEFAULT_CHUNK_SIZE: Int = 1_000_000
        /** About how many bytes one snapshot query should return. */
        const val QUERY_TARGET_BYTES: Long = 1L shl 30
    }
}
