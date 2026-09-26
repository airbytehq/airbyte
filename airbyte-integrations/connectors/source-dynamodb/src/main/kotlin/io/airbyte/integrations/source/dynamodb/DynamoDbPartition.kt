/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigDecimal
import java.time.LocalDate
import java.time.format.DateTimeParseException
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.DescribeTableRequest
import software.amazon.awssdk.services.dynamodb.model.ScanRequest
import software.amazon.awssdk.services.dynamodb.model.TableDescription

private val log = KotlinLogging.logger {}

/** What the partitions creator does for a stream in one round. */
sealed interface DynamoDbReadPlan {
    /** Nothing (left) to read. */
    data object Done : DynamoDbReadPlan

    /** One partition per segment of the table that is not complete yet. */
    data class Scan(val partitions: List<DynamoDbPartition>) : DynamoDbReadPlan

    /**
     * Every segment is complete but the state the CDK applied last predates that: one partition
     * that reads nothing and emits the terminal state (see [DynamoDbTableScan.terminalStateApplied]
     * ).
     */
    data class Finalize(
        val stream: Stream,
        val scan: DynamoDbTableScan,
        val cursor: DynamoDbCursor?,
    ) : DynamoDbReadPlan
}

/**
 * What one [DynamoDbPartitionReader] does: scan one parallel-scan [segment] of one table (the rest
 * of it from the segment's saved key) with the configured attributes projected and, for an
 * incremental stream, the cursor filter applied.
 *
 * A table is split into [DynamoDbTableScan.totalSegments] segments sized from `DescribeTable`
 * (`Segment`/`TotalSegments`: DynamoDB hashes the partition key, no boundary has to be computed).
 * Measured on a 1 GB table, 16 segments read 10x faster than one for the same consumed capacity.
 * Tables are also read concurrently with each other; the `concurrency` setting bounds how many
 * segments and tables scan at once.
 */
data class DynamoDbPartition(
    val stream: Stream,
    /** The attributes to read, in projection order: the configured stream's fields. */
    val attributes: List<String>,
    /** Cursor filter of an incremental stream that has a saved cursor; null for a full scan. */
    val filter: DynamoDbCursorFilter?,
    /** Cursor bookkeeping of an incremental stream; null for a full refresh. */
    val cursor: DynamoDbCursor?,
    /** Progress of the whole table, shared with the other segments' partitions. */
    val scan: DynamoDbTableScan,
    /** The segment this partition reads, `0 <= segment < scan.totalSegments`. */
    val segment: Int,
    /**
     * True for the last partition of the round: its checkpoint is the one the CDK applies last, so
     * its reader waits for the round's other readers to stop before taking it.
     */
    val lastInRound: Boolean,
) {
    val totalSegments: Int
        get() = scan.totalSegments

    /**
     * The `Scan` request, without `ExclusiveStartKey`. Every attribute is referenced through a
     * placeholder (`#a0`, `#a1`, ...) mapped in `ExpressionAttributeNames`, so that reserved words
     * and names with special characters need no configuration (the legacy connector only aliased
     * the names listed in `reserved_attribute_names`).
     */
    fun scanRequest(pageLimit: Int): ScanRequest {
        val names = LinkedHashMap<String, String>()
        attributes.forEachIndexed { i: Int, attribute: String -> names["#a$i"] = attribute }
        val builder: ScanRequest.Builder =
            ScanRequest.builder()
                .tableName(stream.name)
                .projectionExpression(names.keys.joinToString(", "))
                .expressionAttributeNames(names)
        if (filter != null) {
            // The cursor is one of the configured fields, so it is always projected.
            val alias: String = names.entries.first { it.value == filter.attribute }.key
            builder
                .filterExpression("$alias ${filter.comparator} :cursor")
                .expressionAttributeValues(mapOf(":cursor" to filter.attributeValue()))
        }
        if (totalSegments > 1) {
            builder.segment(segment).totalSegments(totalSegments)
        }
        if (pageLimit > 0) {
            builder.limit(pageLimit)
        }
        return builder.build()
    }

    companion object {
        /** Plans the round for the stream's current state and the progress made so far. */
        fun plan(
            feedBootstrap: StreamFeedBootstrap,
            sharedState: DynamoDbSharedState,
        ): DynamoDbReadPlan {
            val stream: Stream = feedBootstrap.feed
            if (sharedState.isComplete(stream.id)) {
                return DynamoDbReadPlan.Done
            }
            val state: DynamoDbStreamStateValue? =
                DynamoDbStreamStateValue.parse(stream.id, feedBootstrap.currentState)
            val attributes: List<String> = stream.fields.map { it.id }
            val filter: DynamoDbCursorFilter?
            val cursor: DynamoDbCursor?
            val resume: DynamoDbStreamStateValue.ScanProgress?
            when (stream.configuredSyncMode) {
                ConfiguredSyncMode.FULL_REFRESH -> {
                    if (state?.scanComplete == true) {
                        log.info {
                            "Stream ${stream.id} was read to the end already; nothing to do."
                        }
                        sharedState.markComplete(stream.id)
                        return DynamoDbReadPlan.Done
                    }
                    // Any other saved state (a legacy incremental cursor, say) is ignored: a full
                    // refresh reads the whole table. Only the progress of an interrupted full
                    // refresh (a scan without cursor) is resumed.
                    filter = null
                    cursor = null
                    resume = state?.scan?.takeIf { state.cursorField == null }
                }
                ConfiguredSyncMode.INCREMENTAL -> {
                    val cursorField: EmittedField =
                        stream.configuredCursor as? EmittedField
                            ?: throw ConfigErrorException(
                                "Stream '${stream.id}' is configured for incremental sync without a cursor attribute.",
                            )
                    val cursorType: DynamoDbCursorType = DynamoDbCursorType.of(stream, cursorField)
                    // Like the legacy connector's CursorManager: a saved cursor applies only when
                    // the cursor attribute did not change, otherwise the stream starts over.
                    val savedState: DynamoDbStreamStateValue? =
                        when {
                            state == null -> null
                            state.cursorField == listOf(cursorField.id) -> state
                            else -> {
                                log.info {
                                    "Stream ${stream.id}: the cursor attribute changed from " +
                                        "${state.cursorField} to [${cursorField.id}]; " +
                                        "ignoring the saved cursor and reading the whole table."
                                }
                                null
                            }
                        }
                    val lowerBound: String? = savedState?.cursor
                    filter =
                        lowerBound?.let { DynamoDbCursorFilter(cursorField.id, cursorType, it) }
                    cursor =
                        DynamoDbCursor(
                            field = cursorField.id,
                            type = cursorType,
                            lowerBound = lowerBound,
                            lowerBoundRecordCount = savedState?.cursorRecordCount ?: 0L,
                            inclusiveLowerBound = filter?.inclusive ?: false,
                        )
                    resume = savedState?.scan
                }
            }
            val tableScan: DynamoDbTableScan =
                sharedState.tableScan(stream.id) {
                    val saved: List<DynamoDbStreamStateValue.SegmentProgress>? =
                        resume?.segmentProgress()
                    val totalSegments: Int =
                        if (saved != null) resume.segmentCount()
                        else segmentCount(stream, sharedState)
                    DynamoDbTableScan(stream, totalSegments, saved)
                }
            if (tableScan.isComplete()) {
                if (tableScan.terminalStateApplied) {
                    sharedState.markComplete(stream.id)
                    return DynamoDbReadPlan.Done
                }
                return DynamoDbReadPlan.Finalize(stream, tableScan, cursor)
            }
            val incomplete: List<Int> = tableScan.incompleteSegments()
            tableScan.beginRound()
            log.info {
                "Planned a scan of table '${stream.name}': ${incomplete.size} of " +
                    "${tableScan.totalSegments} segment(s) left" +
                    (filter?.let { " with ${it.attribute} ${it.comparator} '${it.value}'" } ?: "")
            }
            return DynamoDbReadPlan.Scan(
                incomplete.mapIndexed { i: Int, segment: Int ->
                    DynamoDbPartition(
                        stream = stream,
                        attributes = attributes,
                        filter = filter,
                        cursor = cursor,
                        scan = tableScan,
                        segment = segment,
                        lastInRound = i == incomplete.lastIndex,
                    )
                },
            )
        }

        /** Sizes the table's segment count from `DescribeTable`; no scan involved. */
        private fun segmentCount(stream: Stream, sharedState: DynamoDbSharedState): Int {
            val table: TableDescription =
                sharedState.client
                    .describeTable(DescribeTableRequest.builder().tableName(stream.name).build())
                    .table()
            val sizeBytes: Long = table.tableSizeBytes() ?: 0L
            val count: Int =
                DynamoDbTableScan.segmentCount(
                    sizeBytes,
                    sharedState.segmentTargetBytes,
                    sharedState.maxSegments,
                    unknownSizeSegments = sharedState.configuration.maxConcurrency,
                )
            log.info {
                "Table '${stream.name}' is $sizeBytes bytes according to DescribeTable" +
                    (if (sizeBytes <= 0L) " (not refreshed yet, or empty)" else "") +
                    "; scanning it in $count segment(s)."
            }
            return count
        }
    }
}

/**
 * How an incremental cursor attribute is filtered and compared. Only strings (`S`, e.g. ISO 8601
 * timestamps) and numbers (`N`, e.g. epoch values) are supported, as with the legacy connector.
 */
enum class DynamoDbCursorType {
    S,
    N;

    fun attributeValue(text: String): AttributeValue =
        when (this) {
            S -> AttributeValue.fromS(text)
            N -> AttributeValue.fromN(text)
        }

    /**
     * Compares two cursor values: strings lexicographically, numbers numerically (the legacy
     * connector compared numbers as doubles; DynamoDB numbers have 38 digits, so [BigDecimal]). A
     * number that does not parse falls back to a string comparison.
     */
    fun compare(a: String, b: String): Int =
        when (this) {
            S -> a.compareTo(b)
            N -> {
                val x: BigDecimal? = a.toBigDecimalOrNull()
                val y: BigDecimal? = b.toBigDecimalOrNull()
                if (x != null && y != null) x.compareTo(y) else a.compareTo(b)
            }
        }

    companion object {
        /**
         * The cursor type from the cursor attribute's schema in the configured catalog, the way the
         * legacy connector picked its filter type: `string` cursors are `S`, `integer` and `number`
         * cursors are `N`. Accepts the canonical shapes this connector discovers (`{"type":
         * "string"}`, `{"type": "number", "airbyte_type": "integer"}`, `{"type": "number"}`) and
         * the legacy `["null", <type>]` shapes of a catalog configured before them. (The legacy
         * connector accepted `number` only with `airbyte_type: integer` and, because of a bug,
         * failed on every `integer` cursor.)
         */
        fun of(stream: Stream, cursorField: EmittedField): DynamoDbCursorType {
            val fieldType: DynamoDbFieldType =
                cursorField.type as? DynamoDbFieldType
                    ?: throw ConfigErrorException(
                        "Stream '${stream.id}': unexpected type of cursor attribute '${cursorField.id}'.",
                    )
            val jsonType: JsonNode? = fieldType.jsonSchema().get("type")
            val types: Set<String> =
                when {
                    jsonType == null -> emptySet()
                    jsonType.isTextual -> setOf(jsonType.asText())
                    jsonType.isArray -> jsonType.map { it.asText() }.filter { it != "null" }.toSet()
                    else -> emptySet()
                }
            return when (types) {
                setOf("string") -> S
                setOf("integer"),
                setOf("number") -> N
                else ->
                    throw ConfigErrorException(
                        "Stream '${stream.id}': the cursor attribute '${cursorField.id}' has type " +
                            "${jsonType ?: "unknown"}; only string and number attributes can be " +
                            "used as a cursor.",
                    )
            }
        }
    }
}

/** `FilterExpression` of an incremental scan: `cursor > :saved` (or `>=`, see [comparator]). */
data class DynamoDbCursorFilter(
    val attribute: String,
    val type: DynamoDbCursorType,
    val value: String,
) {
    /**
     * True for a bare date such as `2016-02-15`: the filter is then `>=`, so that the items of the
     * day of the last sync are not skipped; `>` otherwise. Same rule as the legacy connector.
     */
    val inclusive: Boolean
        get() = isBareDate(value)

    val comparator: String
        get() = if (inclusive) ">=" else ">"

    fun attributeValue(): AttributeValue = type.attributeValue(value)

    companion object {
        fun isBareDate(value: String): Boolean =
            try {
                LocalDate.parse(value)
                true
            } catch (_: DateTimeParseException) {
                false
            }
    }
}

/**
 * Cursor bookkeeping of an incremental scan: the lower bound the scan filters on (the saved
 * cursor), and how the running maxima of the segments become the next cursor once every segment is
 * complete. A maximum is not a safe cursor before that: a `Scan` returns items in key order, not in
 * cursor order.
 */
data class DynamoDbCursor(
    val field: String,
    val type: DynamoDbCursorType,
    val lowerBound: String?,
    val lowerBoundRecordCount: Long,
    /**
     * True when the filter is `>=` (a bare date): the items with the saved cursor value are read
     * and counted again, so the saved record count is not carried over.
     */
    val inclusiveLowerBound: Boolean,
) {
    /**
     * The next cursor: the highest value seen in any segment, with the number of records sharing it
     * summed over the segments. The saved lower bound takes part too, so that the cursor stays
     * where it was when nothing newer was found (like the legacy `StateDecoratingIterator`).
     */
    fun merge(segments: List<DynamoDbTableScan.SegmentCursor>): DynamoDbTableScan.SegmentCursor {
        val saved: DynamoDbTableScan.SegmentCursor? =
            lowerBound?.let {
                DynamoDbTableScan.SegmentCursor(
                    it,
                    if (inclusiveLowerBound) 0L else lowerBoundRecordCount,
                )
            }
        val candidates: List<DynamoDbTableScan.SegmentCursor> =
            segments.filter { it.max != null } + listOfNotNull(saved)
        if (candidates.isEmpty()) {
            return DynamoDbTableScan.SegmentCursor(null, 0L)
        }
        val max: String =
            candidates
                .map { it.max!! }
                .reduce { a: String, b: String -> if (type.compare(a, b) < 0) b else a }
        val count: Long =
            candidates.filter { type.compare(it.max!!, max) == 0 }.sumOf { it.recordCount }
        return DynamoDbTableScan.SegmentCursor(max, count)
    }

    /**
     * Mutable tracker of one segment's running maximum; not thread-safe, a segment is read on one
     * thread. Starts from what the segment had seen when its scan was interrupted, or empty.
     */
    inner class Tracker(initialMax: String?, initialMaxRecordCount: Long) {
        var max: String? = initialMax
            private set

        var maxRecordCount: Long = initialMaxRecordCount
            private set

        /**
         * Accounts for an item. Only `S` and `N` cursor values are compared; an item without the
         * cursor attribute, or with another type, is emitted but does not move the cursor (the
         * legacy connector ignored missing cursors and compared everything else as text).
         */
        fun observe(item: Map<String, AttributeValue>) {
            val value: AttributeValue = item[field] ?: return
            val text: String =
                when (value.type()) {
                    AttributeValue.Type.S -> value.s()
                    AttributeValue.Type.N -> value.n()
                    else -> return
                }
            val current: String? = max
            val comparison: Int = if (current == null) -1 else type.compare(current, text)
            if (comparison < 0) {
                max = text
                maxRecordCount = 1L
            } else if (comparison == 0) {
                maxRecordCount++
            }
        }

        fun cursor(): DynamoDbTableScan.SegmentCursor =
            DynamoDbTableScan.SegmentCursor(max, maxRecordCount)
    }
}
