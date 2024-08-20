/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.MetadataYamlPropertySource.Companion.PROPERTY_PREFIX
import io.airbyte.cdk.output.OutputConsumer
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import kotlinx.coroutines.sync.Semaphore

/** Default implementation of [JdbcSharedState]. */
@Singleton
class DefaultJdbcSharedState(
    override val configuration: JdbcSourceConfiguration,
    override val outputConsumer: OutputConsumer,
    override val selectQuerier: SelectQuerier,
    @Value("\${$PROPERTY_PREFIX.jdbc.with-sampling:$WITH_SAMPLING}")
    override val withSampling: Boolean,
    @Value("\${$PROPERTY_PREFIX.jdbc.table-sample-size:$TABLE_SAMPLE_SIZE}")
    override val maxSampleSize: Int,
    /** How many bytes per second we can expect the database to send to the connector. */
    @Value("\${$PROPERTY_PREFIX.jdbc.throughput-bytes-per-second:$THROUGHPUT_BYTES_PER_SECOND}")
    val expectedThroughputBytesPerSecond: Long,
    /** Smallest possible fetchSize value. */
    @Value("\${$PROPERTY_PREFIX.jdbc.min-fetch-size:$FETCH_SIZE_LOWER_BOUND}")
    val minFetchSize: Int,
    /** Default fetchSize value, in absence of any other estimate. */
    @Value("\${$PROPERTY_PREFIX.jdbc.default-fetch-size:$DEFAULT_FETCH_SIZE}")
    val defaultFetchSize: Int,
    /** Largest possible fetchSize value. */
    @Value("\${$PROPERTY_PREFIX.jdbc.max-fetch-size:$FETCH_SIZE_UPPER_BOUND}")
    val maxFetchSize: Int,
    /** How much of the JVM heap can we fill up with [java.sql.ResultSet] data. */
    @Value("\${$PROPERTY_PREFIX.jdbc.memory-capacity-ratio:$MEM_CAPACITY_RATIO}")
    val memoryCapacityRatio: Double,
    /** Estimated bytes used as overhead for each row in a [java.sql.ResultSet]. */
    @Value("\${$PROPERTY_PREFIX.jdbc.estimated-record-overhead-bytes:$RECORD_OVERHEAD_BYTES}")
    val estimatedRecordOverheadBytes: Long,
    /** Estimated bytes used as overhead for each column value in a [java.sql.ResultSet]. */
    @Value("\${$PROPERTY_PREFIX.jdbc.estimated-field-overhead-bytes:$FIELD_OVERHEAD_BYTES}")
    val estimatedFieldOverheadBytes: Long,
    /** Overrides the JVM heap capacity to provide determinism in tests. */
    val maxMemoryBytesForTesting: Long? = null
) : JdbcSharedState {

    val maxPartitionThroughputBytesPerSecond: Long =
        expectedThroughputBytesPerSecond / configuration.maxConcurrency

    override val targetPartitionByteSize: Long =
        maxPartitionThroughputBytesPerSecond * configuration.checkpointTargetInterval.seconds

    override fun jdbcFetchSizeEstimator(): JdbcSharedState.JdbcFetchSizeEstimator =
        DefaultJdbcFetchSizeEstimator(
            maxMemoryBytes = maxMemoryBytesForTesting ?: Runtime.getRuntime().maxMemory(),
            configuration.maxConcurrency,
            minFetchSize,
            defaultFetchSize,
            maxFetchSize,
            memoryCapacityRatio,
        )

    override fun rowByteSizeEstimator(): JdbcSharedState.RowByteSizeEstimator =
        DefaultRowByteSizeEstimator(estimatedRecordOverheadBytes, estimatedFieldOverheadBytes)

    internal val semaphore = Semaphore(configuration.maxConcurrency)

    override fun tryAcquireResourcesForCreator(): StreamPartitionsCreator.AcquiredResources? =
        if (semaphore.tryAcquire()) {
            StreamPartitionsCreator.AcquiredResources { semaphore.release() }
        } else {
            null
        }

    override fun tryAcquireResourcesForReader(): StreamPartitionReader.AcquiredResources? =
        if (semaphore.tryAcquire()) {
            StreamPartitionReader.AcquiredResources { semaphore.release() }
        } else {
            null
        }

    companion object {

        // Sampling defaults.
        internal const val WITH_SAMPLING: Boolean = false
        internal const val TABLE_SAMPLE_SIZE: Int = 1024
        internal const val THROUGHPUT_BYTES_PER_SECOND: Long = 10L shl 20

        // fetchSize defaults
        internal const val FETCH_SIZE_LOWER_BOUND: Int = 10
        internal const val DEFAULT_FETCH_SIZE: Int = 1_000
        internal const val FETCH_SIZE_UPPER_BOUND: Int = 10_000_000

        // Memory estimate defaults.
        internal const val RECORD_OVERHEAD_BYTES = 16L
        internal const val FIELD_OVERHEAD_BYTES = 16L
        // We're targeting use of 60% of the available memory in order to allow
        // for some headroom for other garbage collection.
        internal const val MEM_CAPACITY_RATIO: Double = 0.6
    }
}
