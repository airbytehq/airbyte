/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.File
import java.nio.file.FileSystem
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths
import java.time.Instant

/** Default implementation of [JdbcSharedState]. */
@Singleton
class DefaultJdbcSharedState(
    override val configuration: JdbcSourceConfiguration,
    override val selectQuerier: SelectQuerier,
    val constants: DefaultJdbcConstants,
    internal val concurrencyResource: ConcurrencyResource,
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

    override val targetPartitionByteSize: Long = 400L shl 20 // TEMP: hardcode partition size to 1GB
//        maxPartitionThroughputBytesPerSecond * configuration.checkpointTargetInterval.seconds

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

    private val log = KotlinLogging.logger {}
    override fun tryAcquireResourcesForReader(): JdbcPartitionReader.AcquiredResources? {

        log.info { "Skipping staging area inspection" }

        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire() ?: return null
        return JdbcPartitionReader.AcquiredResources { acquiredThread.close() }
    }
}
