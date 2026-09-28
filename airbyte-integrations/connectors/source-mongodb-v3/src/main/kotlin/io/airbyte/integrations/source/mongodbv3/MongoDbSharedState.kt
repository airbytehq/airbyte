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
import java.util.concurrent.ConcurrentHashMap

/**
 * Holds the state shared by all partition creators and readers of a READ: the configuration, a
 * single long-lived [MongoClient], and the CDK's resource semaphores. Mirrors `DataGenSharedState`.
 */
@Singleton
class MongoDbSharedState(
    val configuration: MongoDbSourceConfiguration,
    val concurrencyResource: ConcurrencyResource,
    val resourceAcquirer: ResourceAcquirer,
    /**
     * Test hook: cap the records a snapshot partition reads per `run()` so mid-collection resume
     * can be exercised without waiting for the `checkpointTargetInterval` timeout. `0` means
     * unlimited.
     */
    @Value("\${airbyte.connector.extract.mongodb.max-records-per-run:0}")
    val maxRecordsPerRun: Long = 0,
) {
    /** One client for the whole READ; MongoDB pools connections internally. */
    val client: MongoClient by lazy { MongoDbClientFactory.create(configuration) }

    /**
     * Snapshot streams that finished reading in this READ, so the factory stops re-planning them.
     */
    val completedSnapshots: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    fun tryAcquireResourcesForCreator(): CreatorAcquiredResources? {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire() ?: return null
        return CreatorAcquiredResources { acquiredThread.close() }
    }

    fun tryAcquireResourcesForReader(
        resourceTypes: List<ResourceType>,
    ): Map<ResourceType, ReaderAcquiredResource>? {
        val acquiredResources: Map<ResourceType, Resource.Acquired> =
            resourceAcquirer.tryAcquire(resourceTypes) ?: return null
        return acquiredResources
            .map { (type: ResourceType, acquired: Resource.Acquired) ->
                type to
                    object : ReaderAcquiredResource {
                        override val resource: Resource.Acquired = acquired
                        override fun close() = acquired.close()
                    }
            }
            .toMap()
    }

    @PreDestroy
    fun close() {
        client.close()
    }
}

/** Resource a partitions creator holds while planning (one [ConcurrencyResource] permit). */
fun interface CreatorAcquiredResources : AutoCloseable

/** Resource a partition reader holds while reading (a DB connection / output socket slot). */
interface ReaderAcquiredResource : AutoCloseable {
    val resource: Resource.Acquired?
}
