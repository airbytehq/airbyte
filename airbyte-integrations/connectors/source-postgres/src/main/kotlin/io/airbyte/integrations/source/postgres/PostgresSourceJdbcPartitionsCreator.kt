/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.read.JdbcConcurrentPartitionsCreator
import io.airbyte.cdk.read.JdbcCursorPartition
import io.airbyte.cdk.read.JdbcNonResumablePartitionReader
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.JdbcPartitionsCreator
import io.airbyte.cdk.read.JdbcPartitionsCreatorFactory
import io.airbyte.cdk.read.JdbcSharedState
import io.airbyte.cdk.read.JdbcSplittablePartition
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.MODE_PROPERTY
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Sample
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.querySingleValue
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator.Companion.toQualifiedTableName
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlin.random.Random
import kotlin.use

@Singleton
@Primary
@Requires(property = MODE_PROPERTY, value = "concurrent")
class PostgresSourceConcurrentJdbcPartitionsCreatorFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    partitionFactory: JdbcPartitionFactory<A, S, P>,
) : JdbcPartitionsCreatorFactory<A, S, P>(partitionFactory) {
    override fun partitionsCreator(partition: P): JdbcPartitionsCreator<A, S, P> =
        PostgresSourceJdbcConcurrentPartitionsCreator(partition, partitionFactory)
}

class PostgresSourceJdbcConcurrentPartitionsCreator<
    A : JdbcSharedState, S : JdbcStreamState<A>, P : JdbcPartition<S>>(
    partition: P,
    partitionFactory: JdbcPartitionFactory<A, S, P>,
) : JdbcConcurrentPartitionsCreator<A, S, P>(partition, partitionFactory) {
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
        // Sample the table for partition split boundaries and for record byte sizes.
        val sample: Sample<Pair<OpaqueStateValue?, Long>> =
            collectSample { record: SelectQuerier.ResultRow ->
                val boundary: OpaqueStateValue? =
                    (partition as? JdbcSplittablePartition<*>)?.incompleteState(record)
                val rowByteSize: Long =
                    sharedState.rowByteSizeEstimator().apply(record.data.toJson())
                boundary to rowByteSize
            }
        if (sample.kind == Sample.Kind.EMPTY) {
            log.info { "Sampling query found that the table was empty." }
            return listOf(CheckpointOnlyPartitionReader())
        }
        val rowByteSizeSample: Sample<Long> = sample.map { (_, rowByteSize: Long) -> rowByteSize }
        streamState.fetchSize = sharedState.jdbcFetchSizeEstimator().apply(rowByteSizeSample)
        val expectedTableByteSize: Long = totalRelationSize(stream)
        log.info { "Table memory size estimated at ${expectedTableByteSize shr 20} MiB." }
        // Handle edge case where the table can't be split.
        if (partition !is JdbcSplittablePartition<*>) {
            log.warn {
                "Table cannot be read by concurrent partition readers because it cannot be split."
            }
            return listOf(JdbcNonResumablePartitionReader(partition))
        }
        // Happy path.
        log.info { "Target partition size is ${sharedState.targetPartitionByteSize shr 20} MiB." }
        val secondarySamplingRate: Double =
            if (expectedTableByteSize <= sharedState.targetPartitionByteSize) {
                0.0
            } else {
                val expectedPartitionByteSize: Long =
                    expectedTableByteSize / sharedState.maxSampleSize
                if (expectedPartitionByteSize < sharedState.targetPartitionByteSize) {
                    expectedPartitionByteSize.toDouble() / sharedState.targetPartitionByteSize
                } else {
                    1.0
                }
            }
        val random = Random(expectedTableByteSize) // RNG output is repeatable.
        val splitBoundaries: List<OpaqueStateValue> =
            sample.sampledValues
                .filter { random.nextDouble() < secondarySamplingRate }
                .mapNotNull { (splitBoundary: OpaqueStateValue?, _) -> splitBoundary }
                .distinct()

        // Handle edge case with empty split boundaries when sampling rate is too low,
        // causing random filtering to discard all sampled boundaries, which would
        // lead to division by zero the in the split() function. Fall back to single partition.
        if (splitBoundaries.isEmpty()) {
            log.warn { "No split boundaries found, using single partition" }
            return listOf(JdbcNonResumablePartitionReader(partition))
        }
        val partitions: List<JdbcPartition<*>> = partitionFactory.split(partition, splitBoundaries)
        log.info { "Table will be read by ${partitions.size} concurrent partition reader(s)." }
        return partitions.map { JdbcNonResumablePartitionReader(it) }
    }

    /** Get total relation size in bytes for a given table - this includes toast data. */
    @SuppressFBWarnings(
        value = ["SQL_PREPARED_STATEMENT_GENERATED_FROM_NONCONSTANT_STRING"],
        justification = "testing"
    )
    private fun totalRelationSize(stream: Stream): Long {
        val sql = "SELECT pg_total_relation_size(?)"
        return querySingleValue(
            JdbcConnectionFactory(sharedState.configuration),
            sql,
            { stmt -> stmt.setString(1, toQualifiedTableName(stream.namespace, stream.name)) },
            { rs ->
                return@querySingleValue rs.getLong(1)
            }
        )
    }
}
