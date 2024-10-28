/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.output.OutputConsumer
import io.micronaut.context.annotation.DefaultImplementation
import java.time.Instant

/**
 * Encapsulates database-specific state, both constant or transient, common to all partitions.
 *
 * Implementations should be thread-safe.
 */
@DefaultImplementation(DefaultJdbcSharedState::class)
interface JdbcSharedState {

    /** Configuration for the JDBC source connector. */
    val configuration: JdbcSourceConfiguration

    /** Where the records get dumped into. */
    val outputConsumer: OutputConsumer

    /** Queries the database. */
    val selectQuerier: SelectQuerier

    /** Is sampling the streams a good idea? */
    val withSampling: Boolean

    /** Sample size limit. */
    val maxSampleSize: Int

    /** Targeted memory footprint of a partition, in bytes. */
    val targetPartitionByteSize: Long

    /** Keeping the time when the read operation started. */
    val snapshotReadStartTime: Instant

    /** Creates a new instance of a [JdbcFetchSizeEstimator]. */
    fun jdbcFetchSizeEstimator(): JdbcFetchSizeEstimator

    fun interface JdbcFetchSizeEstimator {
        /** Estimates a good JDBC fetchSize value based on a [rowByteSizeSample]. */
        fun apply(rowByteSizeSample: Sample<Long>): Int
    }

    /** Creates a new instance of a [RowByteSizeEstimator]. */
    fun rowByteSizeEstimator(): RowByteSizeEstimator

    fun interface RowByteSizeEstimator {
        /** Estimates the memory footprint of a row based on its corresponding [record]. */
        fun apply(record: ObjectNode): Long
    }

    /** Tries to acquire global resources for [JdbcPartitionsCreator]. */
    fun tryAcquireResourcesForCreator(): JdbcPartitionsCreator.AcquiredResources?

    /** Tries to acquire global resources for [JdbcPartitionReader]. */
    fun tryAcquireResourcesForReader(): JdbcPartitionReader.AcquiredResources?
}
