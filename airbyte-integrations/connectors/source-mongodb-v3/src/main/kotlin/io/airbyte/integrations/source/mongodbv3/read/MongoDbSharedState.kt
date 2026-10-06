/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read

import com.mongodb.client.MongoClient
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.integrations.source.mongodbv3.config.MongoDbClientFactory
import io.airbyte.integrations.source.mongodbv3.config.MongoDbSourceConfiguration
import io.micronaut.context.annotation.Value
import jakarta.annotation.PreDestroy
import jakarta.inject.Singleton
import java.time.Duration
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap

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

    /** Snapshot streams that finished in this READ, so the factory stops re-planning them. */
    val completedSnapshots: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /** Incremental snapshots that hit the WASS budget and yielded so the next sync drains CDC. */
    val snapshotYielded: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /** When an incremental snapshot yields to CDC (WASS); fixed on first access for the READ. */
    val snapshotDeadline: Instant by lazy {
        val budget: Duration =
            when {
                maxSnapshotDurationMsOverride != 0L ->
                    Duration.ofMillis(maxSnapshotDurationMsOverride)
                else -> configuration.maxSnapshotReadDuration ?: Duration.ofDays(3650)
            }
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
