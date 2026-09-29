/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoClient
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.micronaut.context.annotation.Value
import jakarta.annotation.PreDestroy
import jakarta.inject.Singleton
import java.time.Duration
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap

/**
 * Holds the state shared by all partition creators and readers of a READ: the configuration, a
 * single long-lived [MongoClient], and the CDK's resource semaphores. Mirrors `DataGenSharedState`.
 */
@Singleton
class MongoDbSharedState(
    val configuration: MongoDbSourceConfiguration,
    private val concurrencyResource: ConcurrencyResource,
    private val resourceAcquirer: ResourceAcquirer,
    /**
     * Test hook: cap the records a snapshot partition reads per `run()` so mid-collection resume
     * can be exercised without waiting for the `checkpointTargetInterval` timeout. `0` means
     * unlimited.
     */
    @Value("\${airbyte.connector.extract.mongodb.max-records-per-run:0}")
    val maxRecordsPerRun: Long = 0,
    /**
     * Test hook: override the WASS snapshot time budget (see [snapshotDeadline]) in milliseconds so
     * the yield behaviour can be exercised quickly. `0` means use [MongoDbSourceConfiguration]'s
     * `maxSnapshotReadDuration`; a negative value puts the deadline in the past so an incremental
     * snapshot yields right after its first record.
     */
    @Value("\${airbyte.connector.extract.mongodb.max-snapshot-duration-ms:0}")
    private val maxSnapshotDurationMsOverride: Long = 0,
) {
    /** One client for the whole READ; MongoDB pools connections internally. */
    val client: MongoClient by lazy { MongoDbClientFactory.create(configuration) }

    /**
     * Snapshot streams that finished reading in this READ, so the factory stops re-planning them.
     */
    val completedSnapshots: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /**
     * Incremental snapshot streams that hit the WASS snapshot time budget in this READ and yielded
     * so the next sync's change-stream read can advance the resume token before the snapshot
     * resumes.
     */
    val snapshotYielded: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /**
     * The wall-clock instant after which an incremental snapshot should yield to CDC (WASS). Fixed
     * on first access for the whole READ; effectively unlimited when no cap is configured.
     */
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
