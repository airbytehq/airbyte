/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.output.OutputConsumer
import jakarta.inject.Singleton
import kotlinx.coroutines.sync.Semaphore

/** Default implementation of [JdbcSharedState]. */
@Singleton
class DefaultJdbcSharedState(
    override val configuration: JdbcSourceConfiguration,
    override val outputConsumer: OutputConsumer,
    override val selectQuerier: SelectQuerier,
    val constants: DefaultJdbcConstants,
) : JdbcSharedState {

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

    internal val semaphore = Semaphore(configuration.maxConcurrency)

    override fun tryAcquireResourcesForCreator(): JdbcPartitionsCreator.AcquiredResources? =
        if (semaphore.tryAcquire()) {
            JdbcPartitionsCreator.AcquiredResources { semaphore.release() }
        } else {
            null
        }

    override fun tryAcquireResourcesForReader(): JdbcPartitionReader.AcquiredResources? =
        if (semaphore.tryAcquire()) {
            JdbcPartitionReader.AcquiredResources { semaphore.release() }
        } else {
            null
        }
}
