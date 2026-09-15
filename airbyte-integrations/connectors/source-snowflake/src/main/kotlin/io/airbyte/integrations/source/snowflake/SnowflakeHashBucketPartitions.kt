/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.DataField
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.DefaultJdbcCursorIncrementalPartition
import io.airbyte.cdk.read.DefaultJdbcPartition
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcSplittablePartition
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.DefaultJdbcUnsplittablePartition
import io.airbyte.cdk.read.DefaultUnsplittableJdbcCursorIncrementalPartition
import io.airbyte.cdk.read.Equal
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.JdbcConcurrentPartitionsCreator
import io.airbyte.cdk.read.JdbcCursorPartition
import io.airbyte.cdk.read.JdbcNonResumablePartitionReader
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.JdbcPartitionReader
import io.airbyte.cdk.read.JdbcPartitionsCreator
import io.airbyte.cdk.read.JdbcPartitionsCreatorFactory
import io.airbyte.cdk.read.JdbcSharedState
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.MODE_PROPERTY
import io.airbyte.cdk.read.NoWhere
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.Sample
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.WhereClauseNode
import io.airbyte.cdk.read.WhereNode
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.time.Duration
import java.time.Instant
import java.util.UUID
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

/*
 * Splitting big reads into smaller queries.
 *
 * When a query returns a lot of data, Snowflake stores the result in chunks and gives the JDBC
 * driver temporary links to download them. The links expire after about 6 hours and the driver
 * never renews them. If Airbyte takes longer than that to pull the result down (usually because the
 * destination is slow), the download fails with
 * `Max retry reached for the download of chunk#N ... HTTP status=403` and the sync gets nowhere.
 *
 * The fix: if a read looks bigger than [SAFE_QUERY_BYTES], split it into n smaller queries using
 * `MOD(ABS(HASH(col, ...)), n) = ?`. Every row lands in exactly one of the n queries, and each
 * query is small enough to download before its links expire. This is done for every kind of read.
 * Reads of a cursor window run their n queries in parallel; full-table reads run them one after
 * another.
 */

/**
 * A piece of SQL that stands in for a column. The CDK query model cannot be given new node types,
 * but any [DataField] can go where a column goes, and [SnowflakeSourceOperations] writes these out
 * as-is instead of quoting them like a column name.
 */
sealed interface SnowflakeSqlExpression : DataField

/** `COUNT(*)`. Used to size a big read when the sample cannot tell us how big it is. */
data object SnowflakeRowCountColumn : SnowflakeSqlExpression {
    override val id: String = "COUNT(*)"
    override val type: FieldType = LongFieldType
}

/**
 * The `MOD(ABS(HASH(col, ...)), bucketCount)` part of the bucket filter. It is compared to an
 * integer, so the bucket number is passed as a query parameter. The columns are listed out because
 * Snowflake only allows `HASH(*)` in a SELECT, not in a WHERE.
 */
data class SnowflakeHashBucketColumn(
    val hashedColumns: List<DataField>,
    val bucketCount: Int,
) : SnowflakeSqlExpression {
    init {
        require(hashedColumns.isNotEmpty()) { "cannot hash-bucket a query with no columns" }
    }
    override val id: String =
        "MOD(ABS(HASH(${hashedColumns.joinToString(", ") { "\"${it.id}\"" }})), $bucketCount)"
    override val type: FieldType = IntFieldType
}

/**
 * Which columns to hash. Any fixed set of columns works: every row still lands in exactly one
 * bucket. The choice only affects how evenly rows spread out, and whether a row stays in the same
 * bucket from one query to the next. A primary key does both well, so use it if there is one.
 * Otherwise hash everything except the cursor. Cursor columns in views are often computed (for
 * example `DATE(MAX(...))`). If that value changed between queries, rows would jump between buckets
 * already read and buckets not yet read, so some rows would be read twice and others missed.
 */
internal fun hashColumnsFor(
    configuredPrimaryKey: List<EmittedField>?,
    configuredCursor: DataOrMetaField?,
    projected: List<DataField>,
): List<DataField> {
    if (!configuredPrimaryKey.isNullOrEmpty()) return configuredPrimaryKey
    val stable: List<DataField> = projected.filter { it.id != configuredCursor?.id }
    return stable.ifEmpty { projected }
}

/** The columns this query selects. Fails if the query is not a plain column list. */
internal val SelectQuerySpec.projectedColumns: List<DataField>
    get() = (select as? SelectColumns)?.columns ?: error("expected a column projection")

/** Adds "and this row is in bucket [bucketIndex] of [bucketCount]" to the WHERE clause. */
internal fun SelectQuerySpec.withHashBucket(
    hashColumns: List<DataField>,
    bucketIndex: Int,
    bucketCount: Int,
): SelectQuerySpec {
    val leaf: WhereClauseNode =
        Equal(SnowflakeHashBucketColumn(hashColumns, bucketCount), Jsons.numberNode(bucketIndex))
    val clause: WhereClauseNode =
        when (val w: WhereNode = where) {
            NoWhere -> leaf
            is Where -> And(w.clause, leaf)
        }
    return copy(where = Where(clause))
}

/** The plain "read everything in this partition" query, for either kind of default partition. */
internal fun DefaultJdbcPartition.nonResumableSpec(): SelectQuerySpec =
    when (this) {
        is DefaultJdbcUnsplittablePartition -> nonResumableQuerySpec
        is DefaultJdbcSplittablePartition -> nonResumableQuerySpec
        else -> error("unexpected partition type ${this::class.qualifiedName}")
    }

/** The partition's read-everything query, restricted to one bucket. */
internal fun DefaultJdbcPartition.hashBucketQuery(bucketIndex: Int, bucketCount: Int): SelectQuery {
    val spec: SelectQuerySpec = nonResumableSpec()
    val stream: Stream = streamState.stream
    val hashColumns: List<DataField> =
        hashColumnsFor(stream.configuredPrimaryKey, stream.configuredCursor, spec.projectedColumns)
    return selectQueryGenerator.generate(
        spec.withHashBucket(hashColumns, bucketIndex, bucketCount).optimize()
    )
}

/** `SELECT COUNT(*)` over the same rows the partition's read-everything query would return. */
internal fun SelectQuerySpec.asRowCount(): SelectQuerySpec =
    copy(select = SelectColumns(listOf(SnowflakeRowCountColumn)))

internal fun DefaultJdbcPartition.rowCountQuery(): SelectQuery =
    selectQueryGenerator.generate(nonResumableSpec().asRowCount().optimize())

/**
 * Estimated bytes in the read. Normally: scale the sample up. But the sample stops at 1024 rows, so
 * every table over ~67M rows gives the same sample and the same too-small estimate. When that
 * happens ([Sample.Kind.LARGE]), ask for a real row count and multiply by the average row size.
 */
internal fun estimateByteSize(sample: Sample<Long>, rowCount: Long?): Long {
    val fromSample: Long = sample.sampledValues.sum() * sample.valueWeight
    if (sample.kind != Sample.Kind.LARGE || rowCount == null || sample.sampledValues.isEmpty()) {
        return fromSample
    }
    val meanRowBytes: Long = sample.sampledValues.sum() / sample.sampledValues.size
    return maxOf(fromSample, rowCount * meanRowBytes)
}

/**
 * How many buckets it takes to keep each query under
 * [SnowflakeHashBucketPartitionsCreator.SAFE_QUERY_BYTES].
 */
internal fun hashBucketCount(expectedByteSize: Long): Int {
    val safe: Long = SnowflakeHashBucketPartitionsCreator.SAFE_QUERY_BYTES
    return ((expectedByteSize + safe - 1) / safe)
        .coerceIn(2L, SnowflakeHashBucketPartitionsCreator.MAX_BUCKET_COUNT.toLong())
        .toInt()
}

/**
 * One bucket of a cursor window. All buckets run at the same time. When a bucket finishes it
 * reports a checkpoint, and the CDK saves checkpoints in bucket order. So every bucket except the
 * last reports "still at the start of the window", and only the last reports "window done". If any
 * bucket fails, the next sync starts the window again: some rows may be read twice, none are lost.
 */
class SnowflakeHashBucketPartition(
    val parent: DefaultJdbcPartition,
    val cursor: EmittedField,
    val cursorLowerBound: JsonNode,
    val bucketIndex: Int,
    val bucketCount: Int,
) : JdbcPartition<DefaultJdbcStreamState> {

    override val streamState: DefaultJdbcStreamState = parent.streamState

    override val nonResumableQuery: SelectQuery
        get() = parent.hashBucketQuery(bucketIndex, bucketCount)

    override val completeState: OpaqueStateValue
        get() =
            if (bucketIndex < bucketCount - 1) {
                DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(cursor, cursorLowerBound)
            } else {
                parent.completeState
            }

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery =
        parent.samplingQuery(sampleRateInvPow2)
}

/**
 * Runs several queries one after another and only checkpoints when the last one has finished. Used
 * for big full-table reads, which have no way to record "partly done".
 *
 * The CDK's [JdbcPartitionReader] cannot be extended, so this implements [PartitionReader] directly
 * and copies the same resource and output handling.
 */
class SnowflakeMultiQueryPartitionReader(
    val jdbcPartition: JdbcPartition<*>,
    val queries: List<SelectQuery>,
) : PartitionReader {

    private val log = KotlinLogging.logger {}

    val streamState: JdbcStreamState<*> = jdbcPartition.streamState
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val selectQuerier: SelectQuerier = sharedState.selectQuerier

    val runComplete = AtomicBoolean(false)
    val numRecords = AtomicLong()

    private val partitionId: String = UUID.randomUUID().toString().replace("-", "").take(8)
    private val acquiredResources =
        AtomicReference<Map<ResourceType, JdbcPartitionReader.AcquiredResource>>()
    private var outputMessageRouter: OutputMessageRouter? = null
    private lateinit var outputRoute:
        (
            MutableMap<String, FieldValueEncoder<*>>,
            Map<EmittedField, FieldValueChange>?,
        ) -> Unit

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceTypes: List<ResourceType> =
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                DataChannelMedium.STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
                DataChannelMedium.SOCKET ->
                    listOf(
                        ResourceType.RESOURCE_DB_CONNECTION,
                        ResourceType.RESOURCE_OUTPUT_SOCKET,
                    )
            }
        val resources: Map<ResourceType, JdbcPartitionReader.AcquiredResource> =
            jdbcPartition.tryAcquireResourcesForReader(resourceTypes)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        val router =
            OutputMessageRouter(
                streamState.streamFeedBootstrap.dataChannelMedium,
                streamState.streamFeedBootstrap.dataChannelFormat,
                streamState.streamFeedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                streamState.streamFeedBootstrap,
                resources
                    .filter { it.value.resource != null }
                    .map { it.key to it.value.resource!! }
                    .toMap(),
            )
        outputMessageRouter = router
        outputRoute = router.recordAcceptors[stream.id]!!
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        outputPendingMessages()
        checkMaxReadTimeElapsed()
        for ((index: Int, query: SelectQuery) in queries.withIndex()) {
            log.info {
                "Reading query ${index + 1} / ${queries.size} of partition " +
                    "for '${stream.label}'."
            }
            selectQuerier
                .executeQuery(query, SelectQuerier.Parameters(true, streamState.fetchSizeOrDefault))
                .use { result: SelectQuerier.Result ->
                    for (row in result) {
                        outputRoute(row.data, row.changes)
                        numRecords.incrementAndGet()
                    }
                }
        }
        runComplete.set(true)
    }

    /** Same as the stock reader: send any queued state and status messages first (SOCKET mode). */
    private fun outputPendingMessages() {
        if (streamState.streamFeedBootstrap.dataChannelMedium == DataChannelMedium.STDIO) return
        val router: OutputMessageRouter = outputMessageRouter ?: return
        while (true) {
            when (val pending: Any = PartitionReader.pendingStates.poll() ?: break) {
                is AirbyteStateMessage -> router.acceptNonRecord(pending)
                is AirbyteStreamStatusTraceMessage -> router.acceptNonRecord(pending)
            }
        }
    }

    /** Same as the stock reader: do not start if the sync has used up its snapshot time limit. */
    private fun checkMaxReadTimeElapsed() {
        val max: Duration = sharedState.configuration.maxSnapshotReadDuration ?: return
        if (Duration.between(sharedState.snapshotReadStartTime, Instant.now()) > max) {
            throw TransientErrorException("Shutting down snapshot reader: max duration elapsed")
        }
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        if (!runComplete.get()) {
            throw RuntimeException("cannot checkpoint partially read multi-query partition")
        }
        val checkpointPartitionId: String? =
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                DataChannelMedium.SOCKET -> partitionId
                DataChannelMedium.STDIO -> null
            }
        return PartitionReadCheckpoint(
            jdbcPartition.completeState,
            numRecords.get(),
            checkpointPartitionId,
        )
    }

    override fun releaseResources() {
        outputMessageRouter?.close()
        outputMessageRouter = null
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
    }
}

/**
 * Decides how to read a partition. Big reads are split into hash buckets; everything else is handed
 * to the stock [JdbcConcurrentPartitionsCreator] unchanged.
 */
class SnowflakeHashBucketPartitionsCreator(
    partition: DefaultJdbcPartition,
    partitionFactory:
        JdbcPartitionFactory<DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition>,
) :
    JdbcPartitionsCreator<DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition>(
        partition,
        partitionFactory,
    ) {

    private val log = KotlinLogging.logger {}

    /** The sample taken by this creator. The stock creator reuses it rather than sampling again. */
    private var cachedSample: Sample<SelectQuerier.ResultRow>? = null

    private val delegate:
        JdbcConcurrentPartitionsCreator<
            DefaultJdbcSharedState,
            DefaultJdbcStreamState,
            DefaultJdbcPartition,
        > =
        object :
            JdbcConcurrentPartitionsCreator<
                DefaultJdbcSharedState,
                DefaultJdbcStreamState,
                DefaultJdbcPartition,
            >(partition, partitionFactory) {
            override fun <T> collectSample(
                recordMapper: (SelectQuerier.ResultRow) -> T,
            ): Sample<T> = cachedSample?.map(recordMapper) ?: super.collectSample(recordMapper)
        }

    private fun sampleRows(): Sample<SelectQuerier.ResultRow> =
        collectSample { row: SelectQuerier.ResultRow -> row }.also { cachedSample = it }

    private fun rowByteSizes(sample: Sample<SelectQuerier.ResultRow>): Sample<Long> =
        sample.map { row: SelectQuerier.ResultRow ->
            sharedState.rowByteSizeEstimator().apply(row.data.toJson())
        }

    private fun countRows(p: DefaultJdbcPartition): Long? {
        log.info { "Sample hit its 1024-row limit; counting rows to size the read." }
        val record =
            selectQuerier.executeQuery(p.rowCountQuery()).use {
                if (it.hasNext()) it.next().data.toJson() else null
            }
        val count: Long? = record?.fields()?.asSequence()?.firstOrNull()?.value?.asLong()
        log.info { "Row count is ${count ?: "unknown"}." }
        return count
    }

    override suspend fun run(): List<PartitionReader> {
        val p: DefaultJdbcPartition = partition
        return when (p) {
            is DefaultUnsplittableJdbcCursorIncrementalPartition ->
                runCursorIncremental(p, p.cursor, p.cursorLowerBound)
            is DefaultJdbcCursorIncrementalPartition ->
                runCursorIncremental(p, p.cursor, p.cursorLowerBound)
            // Every kind of full-table read, with or without a primary key. The stock splitter
            // can end up with no split points and fall back to one giant query, so big
            // full-table reads are handled here instead.
            else -> runSnapshot(p)
        }
    }

    /** A big cursor window is read as several buckets in parallel. */
    private suspend fun runCursorIncremental(
        incremental: DefaultJdbcPartition,
        cursor: EmittedField,
        cursorLowerBound: JsonNode,
    ): List<PartitionReader> {
        ensureCursorUpperBound()
        if (streamState.cursorUpperBound == null || streamState.cursorUpperBound?.isNull == true) {
            log.info { "Maximum cursor column value query found that the table was empty." }
            return listOf(CheckpointOnlyPartitionReader())
        }
        if (!sharedState.withSampling) {
            return delegate.run()
        }
        val sample: Sample<Long> = rowByteSizes(sampleRows())
        if (sample.kind == Sample.Kind.EMPTY) {
            log.info { "Sampling query found that the table was empty." }
            return listOf(CheckpointOnlyPartitionReader())
        }
        val expectedByteSize: Long = estimateAndSetFetchSize(incremental, sample)
        if (expectedByteSize <= SAFE_QUERY_BYTES) {
            return delegate.run()
        }
        val bucketCount: Int = bucketCountFor(expectedByteSize)
        log.info {
            "Large cursor window: will be read by $bucketCount concurrent " +
                "hash-bucketed partition readers."
        }
        return (0 until bucketCount).map { bucketIndex: Int ->
            JdbcNonResumablePartitionReader(
                SnowflakeHashBucketPartition(
                    incremental,
                    cursor,
                    cursorLowerBound,
                    bucketIndex,
                    bucketCount,
                )
            )
        }
    }

    /** A big full-table read is done as several buckets, one after another, in a single reader. */
    private suspend fun runSnapshot(p: DefaultJdbcPartition): List<PartitionReader> {
        if (p is JdbcCursorPartition<*>) {
            ensureCursorUpperBound()
            if (
                streamState.cursorUpperBound == null || streamState.cursorUpperBound?.isNull == true
            ) {
                log.info { "Maximum cursor column value query found that the table was empty." }
                return listOf(CheckpointOnlyPartitionReader())
            }
        }
        if (!sharedState.withSampling) {
            return delegate.run()
        }
        val sample: Sample<Long> = rowByteSizes(sampleRows())
        if (sample.kind == Sample.Kind.EMPTY) {
            log.info { "Sampling query found that the table was empty." }
            return listOf(CheckpointOnlyPartitionReader())
        }
        val expectedByteSize: Long = estimateAndSetFetchSize(p, sample)
        if (expectedByteSize <= SAFE_QUERY_BYTES) {
            return delegate.run()
        }
        val bucketCount: Int = bucketCountFor(expectedByteSize)
        log.info {
            "Large snapshot: will be read by one reader running " +
                "$bucketCount sequential hash-bucketed queries."
        }
        val queries: List<SelectQuery> =
            (0 until bucketCount).map { bucketIndex: Int ->
                p.hashBucketQuery(bucketIndex, bucketCount)
            }
        return listOf(SnowflakeMultiQueryPartitionReader(p, queries))
    }

    private fun estimateAndSetFetchSize(p: DefaultJdbcPartition, sample: Sample<Long>): Long {
        streamState.fetchSize = sharedState.jdbcFetchSizeEstimator().apply(sample)
        val rowCount: Long? = if (sample.kind == Sample.Kind.LARGE) countRows(p) else null
        val expectedByteSize: Long = estimateByteSize(sample, rowCount)
        log.info { "Partition size estimated at ${expectedByteSize shr 20} MiB." }
        return expectedByteSize
    }

    private fun bucketCountFor(expectedByteSize: Long): Int = hashBucketCount(expectedByteSize)

    companion object {
        const val MAX_BUCKET_COUNT = 512

        /**
         * Biggest result we let one query return. Small enough to download before Snowflake's links
         * expire, even for a slow destination pulling ~25 KB/s.
         */
        const val SAFE_QUERY_BYTES: Long = 512L shl 20 // 512 MiB
    }
}

/** Takes the place of the CDK's concurrent factory so that big reads get hash-bucketed. */
@Singleton
@Primary
@Requires(property = MODE_PROPERTY, value = "concurrent")
class SnowflakeHashBucketPartitionsCreatorFactory(
    partitionFactory:
        JdbcPartitionFactory<DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition>,
) :
    JdbcPartitionsCreatorFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        DefaultJdbcPartition,
    >(partitionFactory) {

    override fun partitionsCreator(
        partition: DefaultJdbcPartition
    ): JdbcPartitionsCreator<DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition> =
        SnowflakeHashBucketPartitionsCreator(partition, partitionFactory)
}
