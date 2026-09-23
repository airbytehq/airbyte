/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.read.DefaultJdbcPartition
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcSplittablePartition
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.JdbcConcurrentPartitionsCreator
import io.airbyte.cdk.read.JdbcCursorPartition
import io.airbyte.cdk.read.JdbcNonResumablePartitionReader
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.JdbcPartitionsCreator
import io.airbyte.cdk.read.JdbcPartitionsCreatorFactory
import io.airbyte.cdk.read.MODE_PROPERTY
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Sample
import io.airbyte.integrations.source.bigqueryv2.readapi.BigQueryReadApiConstants
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlin.math.ceil

private val log = KotlinLogging.logger {}

/**
 * The number of key ranges to split a table into: `ceil(numBytes / targetBytes)` when the table
 * reports its size in bytes, else `ceil(numRows / targetRows)` when only the row count is known,
 * else 1. Clamped to `[1, maxPartitions]`.
 */
internal fun fallbackPartitionCount(
    numBytes: Long?,
    numRows: Long?,
    targetBytes: Long,
    targetRows: Long,
    maxPartitions: Int,
): Int {
    val raw: Int =
        when {
            numBytes != null && numBytes > 0L ->
                ceil(numBytes.toDouble() / targetBytes.coerceAtLeast(1L).toDouble()).toInt()
            numRows != null && numRows > 0L ->
                ceil(numRows.toDouble() / targetRows.coerceAtLeast(1L).toDouble()).toInt()
            else -> 1
        }
    return raw.coerceIn(1, maxPartitions.coerceAtLeast(1))
}

/**
 * The interior split boundaries from an `APPROX_QUANTILES` result, as the `primary_key` opaque
 * state values [JdbcPartitionFactory.split] expects. `APPROX_QUANTILES(x, n)` returns the min, the
 * interior boundaries and the max in order, so the extremes are dropped; nulls and duplicates
 * (which skewed data produces) are removed, so the resulting partition count can be lower than
 * requested. Fewer than three values means no usable interior boundary, so the table is read as one
 * partition.
 */
internal fun interiorBoundaries(
    quantiles: List<JsonNode>,
    pk: EmittedField,
): List<OpaqueStateValue> {
    if (quantiles.size <= 2) return emptyList()
    return quantiles
        .subList(1, quantiles.size - 1)
        .filterNot { it.isNull }
        .distinct()
        .map { DefaultJdbcStreamStateValue.snapshotCheckpoint(listOf(pk), listOf(it)) }
        .filterNot { it.isNull }
}

/**
 * The concurrent partitions creator for BigQuery's JDBC fallback path (the feeds the Storage Read
 * API declines: views, external/materialized/snapshot tables, the emulator, and every base table
 * when the Read API is off or not permitted).
 *
 * It replaces the toolkit's `TABLESAMPLE`-based split. `TABLESAMPLE SYSTEM` samples whole storage
 * blocks, so its boundaries are skewed (one partition can hold most of the table) and its size
 * estimate is inflated. Instead this creator splits a base table with a single quantile-friendly
 * primary key into balanced key ranges whose boundaries come from `APPROX_QUANTILES` over the key
 * column (which reads only that column) and whose count comes from the table's exact `numBytes` (
 * [BigQueryTableTypes.TableFacts]).
 *
 * Each range is a bounded `WHERE pk > a AND pk <= b` query with no `ORDER BY`, read by a
 * [JdbcNonResumablePartitionReader]; the checkpoints are joined in key order, so a completed range
 * is durable. Note the cost: on BigQuery each range still scans the whole table unless the table is
 * clustered or partitioned on the key (measured 2026-09-22: an unclustered 10% id range read 100%
 * of the bytes; an id-clustered table read 10.9%). The boundary query is cheap (2.05 GiB / 2 s on a
 * 515 GiB table).
 *
 * Tables that are not a single-key splittable snapshot (composite key, no key, a view, a cursor
 * partition with no primary key) are read by one unsplit query, as before. This never issues the
 * `sequential` mode's `ORDER BY pk LIMIT n` chunk, which on BigQuery is a full scan plus a
 * single-worker sort per chunk.
 */
class BigQueryConcurrentPartitionsCreator(
    partition: DefaultJdbcPartition,
    partitionFactory:
        JdbcPartitionFactory<DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition>,
    private val tableTypes: BigQueryTableTypes,
    private val constants: BigQueryReadApiConstants,
    private val operations: BigQuerySourceOperations,
) :
    JdbcConcurrentPartitionsCreator<
        DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition>(
        partition,
        partitionFactory,
    ) {

    override suspend fun run(): List<PartitionReader> {
        // For the initial snapshot of an incremental stream, capture the cursor upper bound first.
        if (partition is JdbcCursorPartition<*>) {
            ensureCursorUpperBound()
            if (
                streamState.cursorUpperBound == null || streamState.cursorUpperBound?.isNull == true
            ) {
                log.info { "'${stream.label}' is empty (no maximum cursor value)." }
                return listOf(CheckpointOnlyPartitionReader())
            }
        }

        val facts: BigQueryTableTypes.TableFacts? = tableTypes.factsOf(stream.id)
        applyFetchSize(facts)

        val splittable: DefaultJdbcSplittablePartition? =
            partition as? DefaultJdbcSplittablePartition
        val primaryKey: List<EmittedField> = stream.configuredPrimaryKey ?: emptyList()
        val pk: EmittedField? = primaryKey.singleOrNull()?.takeIf { it.isQuantileFriendly() }
        if (splittable == null || pk == null || facts == null) {
            log.info {
                "'${stream.label}' is read by a single query " +
                    "(no single quantile-friendly primary key or no size metadata)."
            }
            return listOf(JdbcNonResumablePartitionReader(partition))
        }

        val partitionCount: Int = partitionCount(facts)
        if (partitionCount <= 1) {
            log.info { "'${stream.label}' fits one partition; reading it with a single query." }
            return listOf(JdbcNonResumablePartitionReader(partition))
        }

        val boundaries: List<OpaqueStateValue> = quantileBoundaries(splittable, pk, partitionCount)
        if (boundaries.isEmpty()) {
            log.info {
                "APPROX_QUANTILES found no usable boundaries for '${stream.label}'; " +
                    "reading it with a single query."
            }
            return listOf(JdbcNonResumablePartitionReader(partition))
        }

        val partitions: List<io.airbyte.cdk.read.JdbcPartition<*>> =
            partitionFactory.split(partition, boundaries)
        log.info {
            "'${stream.label}' will be read by ${partitions.size} concurrent partition reader(s), " +
                "split on APPROX_QUANTILES of '${pk.id}'."
        }
        return partitions.map { JdbcNonResumablePartitionReader(it) }
    }

    /**
     * Sets the fetch size from the table's average row size, so no sampling query is needed. Leaves
     * it unset (the toolkit default applies) when the size metadata is missing.
     */
    private fun applyFetchSize(facts: BigQueryTableTypes.TableFacts?) {
        if (streamState.fetchSize != null) return
        val numBytes: Long = facts?.numBytes ?: return
        val numRows: Long = facts?.numRows ?: return
        if (numRows <= 0L) return
        val averageRowBytes: Long = (numBytes / numRows).coerceAtLeast(1L)
        streamState.fetchSize =
            sharedState
                .jdbcFetchSizeEstimator()
                .apply(Sample(listOf(averageRowBytes), Sample.Kind.SMALL, valueWeight = 1L))
    }

    private fun partitionCount(facts: BigQueryTableTypes.TableFacts): Int =
        fallbackPartitionCount(
            facts.numBytes,
            facts.numRows,
            constants.fallbackPartitionTargetBytes,
            constants.fallbackPartitionTargetRows,
            constants.fallbackMaxPartitions,
        )

    /**
     * The `partitionCount - 1` interior quantile boundaries, as the `primary_key` opaque state
     * values [JdbcPartitionFactory.split] expects. `APPROX_QUANTILES` may repeat boundaries on
     * skewed data; duplicates and nulls are dropped, so the resulting partition count can be lower
     * than requested.
     */
    private fun quantileBoundaries(
        splittable: DefaultJdbcSplittablePartition,
        pk: EmittedField,
        partitionCount: Int,
    ): List<OpaqueStateValue> {
        val query =
            operations.approxQuantilesQuery(
                stream.name,
                stream.namespace,
                pk,
                numQuantiles = partitionCount,
                where = splittable.where,
            )
        val values: MutableList<JsonNode> = mutableListOf()
        selectQuerier.executeQuery(query).use { result ->
            for (row in result) {
                val value: JsonNode = row.data.toJson()[pk.id] ?: continue
                values.add(value)
            }
        }
        return interiorBoundaries(values, pk)
    }

    /** The primary key types `APPROX_QUANTILES` can split on and the connector reads losslessly. */
    private fun EmittedField.isQuantileFriendly(): Boolean =
        when (type) {
            BigQueryLongFieldType,
            BigQueryDoubleFieldType,
            BigQueryBigNumericFieldType,
            io.airbyte.cdk.jdbc.BigDecimalFieldType,
            io.airbyte.cdk.jdbc.StringFieldType,
            io.airbyte.cdk.jdbc.OffsetDateTimeFieldType,
            BigQueryDateFieldType,
            BigQueryDateTimeFieldType,
            BigQueryTimeFieldType -> true
            else -> false
        }
}

/**
 * Overrides the toolkit's `@Secondary` concurrent factory (via `@Primary`), so the CDK's
 * `JdbcPartitionCreatorFactorySupplier` builds a [BigQueryConcurrentPartitionsCreator] for the
 * feeds the Storage Read API path declines. Mirrors the `@Primary` override in
 * [BigQueryJdbcPartitionFactory].
 */
@Singleton
@Primary
@Requires(property = MODE_PROPERTY, value = "concurrent")
class BigQueryConcurrentPartitionsCreatorFactory(
    private val bigQueryPartitionFactory: BigQueryJdbcPartitionFactory,
    private val tableTypes: BigQueryTableTypes,
    private val constants: BigQueryReadApiConstants,
    private val operations: BigQuerySourceOperations,
) :
    JdbcPartitionsCreatorFactory<
        DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition>(
        bigQueryPartitionFactory,
    ) {

    override fun partitionsCreator(
        partition: DefaultJdbcPartition
    ): JdbcPartitionsCreator<DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition> =
        BigQueryConcurrentPartitionsCreator(
            partition,
            bigQueryPartitionFactory,
            tableTypes,
            constants,
            operations,
        )
}
