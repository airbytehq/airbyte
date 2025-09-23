/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.partitionobjs

import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.integrations.source.datagen.DataGenSourceConfiguration
import io.airbyte.integrations.source.datagen.partitionops.DataGenPartitionReader
import io.airbyte.integrations.source.datagen.partitionops.DataGenPartitionsCreator
import jakarta.inject.Singleton

@Singleton
class DataGenSharedState(
    val configuration: DataGenSourceConfiguration,
    val concurrencyResource: ConcurrencyResource,
    val resourceAcquirer: ResourceAcquirer
) {
    fun tryAcquireResourcesForCreator(): DataGenPartitionsCreator.AcquiredResources? {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire() ?: return null
        return DataGenPartitionsCreator.AcquiredResources { acquiredThread.close() }
    }

    fun tryAcquireResourcesForReader(
        resourcesTypes: List<ResourceType>
    ): Map<ResourceType, DataGenPartitionReader.AcquiredResource>? {
        val acquiredResources: Map<ResourceType, Resource.Acquired>? =
            resourceAcquirer.tryAcquire(resourcesTypes)
        return acquiredResources
            ?.map {
                it.key to
                    object : DataGenPartitionReader.AcquiredResource {
                        override val resource: Resource.Acquired? = it.value
                        override fun close() {
                            resource?.close()
                        }
                    }
            }
            ?.toMap()
    }
}
