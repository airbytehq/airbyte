/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.JdbcConcurrentPartitionsCreator
import io.airbyte.cdk.read.JdbcCursorPartition
import io.airbyte.cdk.read.JdbcNonResumablePartitionReader
import io.airbyte.cdk.read.JdbcPartitionsCreator
import io.airbyte.cdk.read.JdbcPartitionsCreatorFactory
import io.airbyte.cdk.read.JdbcSplittablePartition
import io.airbyte.cdk.read.MODE_PROPERTY
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.Sample
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.querySingleValue
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator.Companion.toQualifiedTableName
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import kotlin.use

/**
 * Micronaut property bounding the number of CTID range partitions one table is split into. This is
 * a Postgres-only setting: the generic Bulk CDK creator caps the count at the sample size.
 */
const val MAX_PARTITIONS_PROPERTY = "airbyte.connector.extract.postgres.max-partitions"
const val DEFAULT_MAX_PARTITIONS: Int = 16_384

@Singleton
@Primary
@Requires(property = MODE_PROPERTY, value = "concurrent")
class PostgresSourceConcurrentJdbcPartitionsCreatorFactory(
    private val postgresPartitionFactory: PostgresSourceJdbcPartitionFactory,
    @Value("\${$MAX_PARTITIONS_PROPERTY:$DEFAULT_MAX_PARTITIONS}") private val maxPartitions: Int,
) :
    JdbcPartitionsCreatorFactory<
        DefaultJdbcSharedState,
        PostgresSourceJdbcStreamState,
        PostgresSourceJdbcPartition,
    >(postgresPartitionFactory) {

    /**
     * Querying for a table's filenode makes it necessary to acquire a DB connection allowance
     * resource. The acquired handle is returned to the caller rather than stored on this singleton,
     * so concurrent feeds do not overwrite one another's handles.
     */
    override fun tryAcquireResources(): PartitionsCreatorFactory.TryAcquireResourcesResult {
        val acquired: AcquiredResources =
            partitionFactory.sharedState.tryAcquireResourcesForCreatorFactory()
                ?: return PartitionsCreatorFactory.TryAcquireResourcesResult.RetryLater
        return PartitionsCreatorFactory.TryAcquireResourcesResult.ReadyToRun(acquired)
    }

    override fun partitionsCreator(
        partition: PostgresSourceJdbcPartition,
    ): JdbcPartitionsCreator<
        DefaultJdbcSharedState,
        PostgresSourceJdbcStreamState,
        PostgresSourceJdbcPartition,
    > =
        PostgresSourceJdbcConcurrentPartitionsCreator(
            partition,
            postgresPartitionFactory,
            maxPartitions,
        )
}

/**
 * Concurrent partitions creator for Postgres. Unlike the generic [JdbcConcurrentPartitionsCreator],
 * which turns sampled rows into partition boundaries and is therefore capped at the sample size,
 * this creator derives the partition count from the table size on disk and the target partition
 * size, and lets [PostgresSourceJdbcPartitionFactory.split] cut the table into that many CTID page
 * ranges. The sample is only used to estimate the row size, which sizes the JDBC fetch size.
 */
class PostgresSourceJdbcConcurrentPartitionsCreator(
    partition: PostgresSourceJdbcPartition,
    private val postgresPartitionFactory: PostgresSourceJdbcPartitionFactory,
    private val maxPartitions: Int,
) :
    JdbcConcurrentPartitionsCreator<
        DefaultJdbcSharedState,
        PostgresSourceJdbcStreamState,
        PostgresSourceJdbcPartition,
    >(partition, postgresPartitionFactory) {
    private val log = KotlinLogging.logger {}

    override fun <T> collectSample(
        recordMapper: (SelectQuerier.ResultRow) -> T,
    ): Sample<T> {
        val values = mutableListOf<T>()
        val samplingQuery: SelectQuery = partition.samplingQuery(0)
        selectQuerier.executeQuery(samplingQuery).use {
            for (row in it) {
                values.add(recordMapper(row))
            }
        }
        val kind: Sample.Kind = if (values.isEmpty()) Sample.Kind.EMPTY else Sample.Kind.LARGE
        log.info { "Sampled ${values.size} rows in ${kind.name} stream '${stream.label}'." }
        return Sample(values, kind, 0)
    }

    override suspend fun run(): List<PartitionReader> {
        // Ensure that the cursor upper bound is known, if required.
        if (partition is JdbcCursorPartition<*>) {
            ensureCursorUpperBound()
            if (
                streamState.cursorUpperBound == null || streamState.cursorUpperBound?.isNull == true
            ) {
                log.info { "Maximum cursor column value query found that the table was empty." }
                return listOf(CheckpointOnlyPartitionReader())
            }
        }
        // Handle edge case where the table can't be sampled.
        if (!sharedState.withSampling) {
            log.warn {
                "Table cannot be read by concurrent partition readers because it cannot be sampled."
            }
            // TODO: adaptive fetchSize computation?
            return listOf(JdbcNonResumablePartitionReader(partition))
        }
        // Sample rows only to estimate their size, which sizes the JDBC fetchSize. The sample
        // plays no part in partitioning: CTID page ranges are computed from the table size below.
        val rowByteSizeSample: Sample<Long> = collectSample { record: SelectQuerier.ResultRow ->
            sharedState.rowByteSizeEstimator().apply(record.data.toJson())
        }
        if (rowByteSizeSample.kind == Sample.Kind.EMPTY) {
            log.info { "Sampling query found that the table was empty." }
            return listOf(CheckpointOnlyPartitionReader())
        }
        streamState.fetchSize = sharedState.jdbcFetchSizeEstimator().apply(rowByteSizeSample)
        // Handle edge case where the table can't be split.
        if (partition !is JdbcSplittablePartition<*>) {
            log.warn {
                "Table cannot be read by concurrent partition readers because it cannot be split."
            }
            return listOf(JdbcNonResumablePartitionReader(partition))
        }
        // Happy path.
        val tableByteSize: Long = tableSize(stream)
        val targetPartitionByteSize: Long = sharedState.targetPartitionByteSize
        val numPartitions: Int =
            computeNumPartitions(tableByteSize, targetPartitionByteSize, maxPartitions)
        log.info {
            "Table size is $tableByteSize bytes and the target partition size is " +
                "$targetPartitionByteSize bytes: splitting '${stream.label}' into " +
                "$numPartitions partition(s), at most $maxPartitions."
        }
        val partitions: List<PostgresSourceJdbcPartition> =
            postgresPartitionFactory.split(partition, numPartitions)
        log.info { "Table will be read by ${partitions.size} concurrent partition reader(s)." }
        return partitions.map { JdbcNonResumablePartitionReader(it) }
    }

    /**
     * Bytes a snapshot of the table has to read: the main table file plus its TOAST table, free
     * space map and visibility map (`pg_table_size`). Indexes are excluded because a CTID range
     * scan never reads them.
     */
    private fun tableSize(stream: Stream): Long {
        val sql = "SELECT pg_table_size(?)"
        return querySingleValue(
            JdbcConnectionFactory(sharedState.configuration),
            sql,
            { stmt -> stmt.setString(1, toQualifiedTableName(stream.namespace, stream.name)) },
            { rs ->
                return@querySingleValue rs.getLong(1)
            },
        )
    }

    companion object {
        /**
         * Number of partitions needed to keep each one at or below [targetPartitionByteSize]:
         * `ceil(tableByteSize / targetPartitionByteSize)`, clamped to `[1, maxPartitions]`. The cap
         * bounds the per-round bookkeeping in the CDK `FeedReader`, which re-registers a `select`
         * clause for every unfinished partition each time one completes.
         */
        fun computeNumPartitions(
            tableByteSize: Long,
            targetPartitionByteSize: Long,
            maxPartitions: Int,
        ): Int {
            if (tableByteSize <= 0L || targetPartitionByteSize <= 0L || maxPartitions <= 1) {
                return 1
            }
            val needed: Long =
                (tableByteSize + targetPartitionByteSize - 1) / targetPartitionByteSize
            return needed.coerceIn(1L, maxPartitions.toLong()).toInt()
        }
    }
}
