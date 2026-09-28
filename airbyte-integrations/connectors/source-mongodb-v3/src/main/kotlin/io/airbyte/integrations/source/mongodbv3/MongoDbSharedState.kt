/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoClient
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import jakarta.annotation.PreDestroy
import jakarta.inject.Singleton

/**
 * Holds the state shared by all partition creators and readers of a READ: the configuration, a
 * single long-lived [MongoClient], and the CDK's resource semaphores. Mirrors `DataGenSharedState`.
 */
@Singleton
class MongoDbSharedState(
    val configuration: MongoDbSourceConfiguration,
    val concurrencyResource: ConcurrencyResource,
    val resourceAcquirer: ResourceAcquirer,
) {
    /** One client for the whole READ; MongoDB pools connections internally. */
    val client: MongoClient by lazy { MongoDbClientFactory.create(configuration) }

    fun tryAcquireResourcesForCreator(): MongoDbSnapshotPartitionsCreator.AcquiredResources? {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire() ?: return null
        return MongoDbSnapshotPartitionsCreator.AcquiredResources { acquiredThread.close() }
    }

    fun tryAcquireResourcesForReader(
        resourceTypes: List<ResourceType>,
    ): Map<ResourceType, MongoDbSnapshotPartitionReader.AcquiredResource>? {
        val acquiredResources: Map<ResourceType, Resource.Acquired> =
            resourceAcquirer.tryAcquire(resourceTypes) ?: return null
        return acquiredResources
            .map { (type: ResourceType, acquired: Resource.Acquired) ->
                type to
                    object : MongoDbSnapshotPartitionReader.AcquiredResource {
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
