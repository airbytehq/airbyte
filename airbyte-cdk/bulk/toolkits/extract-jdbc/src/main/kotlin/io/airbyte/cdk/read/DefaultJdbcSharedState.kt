/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import jakarta.inject.Singleton
import java.time.Instant

/** Default implementation of [JdbcSharedState]. */
@Singleton
class DefaultJdbcSharedState(
    override val configuration: JdbcSourceConfiguration,
    override val selectQuerier: SelectQuerier,
    val constants: DefaultJdbcConstants,
    val concurrencyResource: ConcurrencyResource,
    val resourceAcquirer: ResourceAcquirer,
) : JdbcSharedState {

    // First hit to the readStartTime initializes the value.
    override val snapshotReadStartTime: Instant by
        lazy(LazyThreadSafetyMode.SYNCHRONIZED) { Instant.now() }
    override val withSampling: Boolean
        get() = constants.withSampling

    override val maxSampleSize: Int
        get() = constants.maxSampleSize

    val maxPartitionThroughputBytesPerSecond: Long =
        constants.expectedThroughputBytesPerSecond / configuration.maxConcurrency

    override val targetPartitionByteSize: Long =
        maxPartitionThroughputBytesPerSecond * configuration.checkpointTargetInterval.seconds

    override fun jdbcFetchSizeEstimator(): JdbcSharedState.JdbcFetchSizeEstimator =
        DefaultJdbcFetchSizeEstimator(
            maxMemoryBytes = constants.maxMemoryBytesForTesting ?: Runtime.getRuntime().maxMemory(),
            configuration.maxConcurrency,
            constants.minFetchSize,
            constants.defaultFetchSize,
            constants.maxFetchSize,
            constants.memoryCapacityRatio,
        )

    override fun rowByteSizeEstimator(): JdbcSharedState.RowByteSizeEstimator =
        DefaultRowByteSizeEstimator(
            constants.estimatedRecordOverheadBytes,
            constants.estimatedFieldOverheadBytes,
        )

    override fun tryAcquireResourcesForCreator(): JdbcPartitionsCreator.AcquiredResources? {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire() ?: return null
        return JdbcPartitionsCreator.AcquiredResources { acquiredThread.close() }
    }

    override fun tryAcquireResourcesForReader(
        resourcesTypes: List<ResourceType>
    ): Map<ResourceType, JdbcPartitionReader.AcquiredResource>? {
        val acquiredResources: Map<ResourceType, Resource.Acquired>? =
            resourceAcquirer.tryAcquire(resourcesTypes)
        return acquiredResources
            ?.map {
                it.key to
                    object : JdbcPartitionReader.AcquiredResource {
                        override val resource: Resource.Acquired? = it.value
                        override fun close() {
                            resource?.close()
                        }
                    }
            }
            ?.toMap()
    }
}
