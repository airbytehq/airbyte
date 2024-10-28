/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.output.OutputConsumer
import jakarta.inject.Singleton
import java.time.Instant

/** Default implementation of [JdbcSharedState]. */
@Singleton
class DefaultJdbcSharedState(
    override val configuration: JdbcSourceConfiguration,
    override val outputConsumer: OutputConsumer,
    override val selectQuerier: SelectQuerier,
    val constants: DefaultJdbcConstants,
    internal val concurrencyResource: ConcurrencyResource,
    private val globalLockResource: GlobalLockResource,
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
        val acquiredLock: GlobalLockResource.AcquiredGlobalLock =
            globalLockResource.tryAcquire() ?: return null
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire()
                ?: run {
                    acquiredLock.close()
                    return null
                }
        return JdbcPartitionsCreator.AcquiredResources {
            acquiredThread.close()
            acquiredLock.close()
        }
    }

    override fun tryAcquireResourcesForReader(): JdbcPartitionReader.AcquiredResources? {
        val acquiredLock: GlobalLockResource.AcquiredGlobalLock =
            globalLockResource.tryAcquire() ?: return null
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire()
                ?: run {
                    acquiredLock.close()
                    return null
                }
        return JdbcPartitionReader.AcquiredResources {
            acquiredThread.close()
            acquiredLock.close()
        }
    }
}
