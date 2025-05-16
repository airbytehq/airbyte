/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.output.sockets.SocketManager
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

    override fun tryAcquireResourcesForReader(resourceTypes: Any): JdbcPartitionReader.AcquiredResources? {
        val reses = resourceAcquirer.tryAcquire(listOf(ResourceType.RESOURCE_DB_CONNECTION,
            ResourceType.RESOURCE_OUTPUT_SOCKET))
        val acquiredThread = reses?.get(ResourceType.RESOURCE_DB_CONNECTION) ?: return null
/*
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire() ?: return null
*/
        return JdbcPartitionReader.AcquiredResources { acquiredThread.close() }
    }
}
