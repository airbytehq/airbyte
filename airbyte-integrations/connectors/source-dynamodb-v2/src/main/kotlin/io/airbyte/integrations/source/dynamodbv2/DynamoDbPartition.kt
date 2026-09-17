/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

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
import software.amazon.awssdk.services.dynamodb.model.ScanRequest

private val log = KotlinLogging.logger {}

/**
 * What one [DynamoDbPartitionReader] does: scan one table (the whole table, or the rest of it from
 * [exclusiveStartKey]) with the configured attributes projected and, for an incremental stream, the
 * cursor filter applied.
 *
 * A stream is always one partition: a DynamoDB parallel scan (`Segment`/`TotalSegments`) would
 * split the table without any boundary computation, but the read capacity of a table is shared by
 * its segments, so the speed-up has to be measured on a real table first (see the skill's DynamoDB
 * page, Stage 5). Tables are still read concurrently with each other, up to `maxConcurrency`.
 */
data class DynamoDbPartition(
    val stream: Stream,
    /** The attributes to read, in projection order: the configured stream's fields. */
    val attributes: List<String>,
    /** Cursor filter of an incremental stream that has a saved cursor; null for a full scan. */
    val filter: DynamoDbCursorFilter?,
    /** `ExclusiveStartKey` to resume an interrupted scan from; null to start from the beginning. */
    val exclusiveStartKey: Map<String, AttributeValue>?,
    /** Cursor bookkeeping of an incremental stream; null for a full refresh. */
    val cursor: DynamoDbCursor?,
) {
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
        if (pageLimit > 0) {
            builder.limit(pageLimit)
        }
        return builder.build()
    }

    companion object {
        /**
         * Plans the partition for the stream's current state, or returns null when there is nothing
         * (left) to read.
         */
        fun plan(
            feedBootstrap: StreamFeedBootstrap,
            sharedState: DynamoDbSharedState,
        ): DynamoDbPartition? {
            val stream: Stream = feedBootstrap.feed
            if (sharedState.isComplete(stream.id)) {
                return null
            }
            val state: DynamoDbStreamStateValue? =
                DynamoDbStreamStateValue.parse(stream.id, feedBootstrap.currentState)
            val attributes: List<String> = stream.fields.map { it.id }
            return when (stream.configuredSyncMode) {
                ConfiguredSyncMode.FULL_REFRESH -> {
                    if (state?.scanComplete == true) {
                        log.info {
                            "Stream ${stream.id} was read to the end already; nothing to do."
                        }
                        return null
                    }
                    // Any other saved state (a legacy incremental cursor, say) is ignored: a full
                    // refresh reads the whole table.
                    DynamoDbPartition(
                        stream,
                        attributes,
                        filter = null,
                        exclusiveStartKey = state?.scan?.exclusiveStartKey?.let(::parseKey),
                        cursor = null,
                    )
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
                    val lowerBoundRecordCount: Long = savedState?.cursorRecordCount ?: 0L
                    val resume: DynamoDbStreamStateValue.ScanProgress? = savedState?.scan
                    val filter: DynamoDbCursorFilter? =
                        lowerBound?.let { DynamoDbCursorFilter(cursorField.id, cursorType, it) }
                    DynamoDbPartition(
                        stream,
                        attributes,
                        filter = filter,
                        exclusiveStartKey = resume?.exclusiveStartKey?.let(::parseKey),
                        cursor =
                            DynamoDbCursor(
                                field = cursorField.id,
                                type = cursorType,
                                lowerBound = lowerBound,
                                lowerBoundRecordCount = lowerBoundRecordCount,
                                // The maximum starts at the saved cursor, as in the legacy
                                // StateDecoratingIterator: with no newer item the cursor stays.
                                // Its record count is kept too, unless the filter is inclusive
                                // and re-reads (and re-counts) the items with that cursor value.
                                initialMax = resume?.maxCursor ?: lowerBound,
                                initialMaxRecordCount = resume?.maxCursorRecordCount
                                        ?: if (filter != null && !filter.inclusive)
                                            lowerBoundRecordCount
                                        else 0L,
                            ),
                    )
                }
            }
        }

        private fun parseKey(node: JsonNode): Map<String, AttributeValue> =
            DynamoDbJson.itemFromDynamoDbJson(node)
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
         * cursors are `N`. (The legacy connector accepted `number` only with `airbyte_type:
         * integer` and, because of a bug, failed on every `integer` cursor.)
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
 * cursor), and the running maximum of the cursor values seen, which becomes the next cursor once
 * the scan is complete. The maximum is not a safe cursor before that: a `Scan` returns items in key
 * order, not in cursor order.
 */
data class DynamoDbCursor(
    val field: String,
    val type: DynamoDbCursorType,
    val lowerBound: String?,
    val lowerBoundRecordCount: Long,
    val initialMax: String?,
    val initialMaxRecordCount: Long,
) {
    /**
     * Mutable tracker for one partition read; not thread-safe, a partition is read on one thread.
     */
    inner class Tracker {
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
    }
}
