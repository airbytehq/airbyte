/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import com.mongodb.client.MongoClient
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.integrations.source.mongodb.config.MongoDbClientFactory
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfiguration
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier
import io.micronaut.context.annotation.Value
import jakarta.annotation.PreDestroy
import jakarta.inject.Singleton
import java.time.Duration
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import org.bson.BsonTimestamp
import org.bson.Document

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
     * The cluster time when the change-stream read started: the CDC reader stops after the first
     * event past it, so a busy cluster cannot keep the READ open forever (changes made during the
     * sync are picked up by the next one). `hello` is unprivileged and answered by `mongos` too.
     */
    val cdcTarget: BsonTimestamp by lazy {
        val hello: Document = client.getDatabase("admin").runCommand(Document("hello", 1))
        hello.get("\$clusterTime", Document::class.java)?.get("clusterTime") as? BsonTimestamp
            ?: hello["operationTime"] as? BsonTimestamp
                ?: BsonTimestamp(Instant.now().epochSecond.toInt(), 0)
    }

    /**
     * Whether the server accepts `fullDocumentBeforeChange` (MongoDB 6.0+): a change stream opened
     * with it on an older server fails with an unrecognized-field error.
     */
    val supportsPreImages: Boolean by lazy {
        val buildInfo: Document = client.getDatabase("admin").runCommand(Document("buildInfo", 1))
        val major: Int = (buildInfo["versionArray"] as? List<*>)?.firstOrNull() as? Int ?: 0
        major >= 6
    }

    private val timeSeriesByStream = ConcurrentHashMap<StreamIdentifier, Boolean>()

    /** Whether the collection is a time-series collection (`listCollections` type). */
    fun isTimeSeries(streamId: StreamIdentifier): Boolean =
        timeSeriesByStream.computeIfAbsent(streamId) {
            MongoDbSourceMetadataQuerier.collectionTypes(client, it.namespace!!, it.name)[
                    it.name,
                ] == MongoDbSourceMetadataQuerier.TIMESERIES_TYPE
        }

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
}
