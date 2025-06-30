/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.BinaryNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.math.BigInteger
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset.UTC
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.DateTimeParseException
import java.time.temporal.ChronoField
import java.util.*
import java.util.concurrent.ConcurrentHashMap

@Primary
@Singleton
class MySqlSourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: MySqlSourceOperations,
    val config: MySqlSourceConfiguration,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        MySqlSourceJdbcPartition,
    > {

    private val log = KotlinLogging.logger {}
    private val streamStates = ConcurrentHashMap<StreamIdentifier, DefaultJdbcStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DefaultJdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            DefaultJdbcStreamState(sharedState, streamFeedBootstrap)
        }

    private fun findPkUpperBound(stream: Stream, pkChosenFromCatalog: List<Field>): JsonNode {
        // find upper bound using maxPk query
        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        val from = From(stream.name, stream.namespace)
        val maxPkQuery = SelectQuerySpec(SelectColumnMaxValue(pkChosenFromCatalog[0]), from)

        jdbcConnectionFactory.get().use { connection ->
            val stmt = connection.prepareStatement(selectQueryGenerator.generate(maxPkQuery).sql)
            val rs = stmt.executeQuery()

            if (rs.next()) {
                val jdbcFieldType = pkChosenFromCatalog[0].type as JdbcFieldType<*>
                val pkUpperBound: JsonNode = jdbcFieldType.get(rs, 1)
                return pkUpperBound
            } else {
                // Table might be empty thus there is no max PK value.
                return Jsons.nullNode()
            }
        }
    }

    private fun coldStart(streamState: DefaultJdbcStreamState): MySqlSourceJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()

        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            if (pkChosenFromCatalog.isEmpty()) {
                return MySqlSourceJdbcNonResumableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }

            val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
            if (sharedState.configuration.global) {
                return MySqlSourceJdbcCdcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = null,
                    upperBound = listOf(upperBound)
                )
            } else {
                return MySqlSourceJdbcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = null,
                    upperBound = listOf(upperBound)
                )
            }
        }

        if (sharedState.configuration.global) {
            return MySqlSourceJdbcCdcSnapshotPartition(
                selectQueryGenerator,
                streamState,
                pkChosenFromCatalog,
                lowerBound = null,
            )
        }

        val cursorChosenFromCatalog: Field =
            stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

        if (pkChosenFromCatalog.isEmpty()) {
            return MySqlSourceJdbcNonResumableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog
            )
        }
        return MySqlSourceJdbcSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            pkChosenFromCatalog,
            lowerBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )
    }

    /**
     * Flowchart:
     * 1. If the input state is null - using coldstart.
     * ```
     *    a. If it's global but without PK, use non-resumable  snapshot.
     *    b. If it's global with PK, use snapshot.
     *    c. If it's not global, use snapshot with cursor.
     * ```
     * 2. If the input state is not null -
     * ```
     *    a. If it's in global mode, JdbcPartitionFactory will not handle this. (TODO)
     *    b. If it's cursor based, it could be either in PK read phase (initial read) or
     *       cursor read phase (incremental read). This is differentiated by the stateType.
     *      i. In PK read phase, use snapshot with cursor. If no PKs were found,
     *         use non-resumable snapshot with cursor.
     *      ii. In cursor read phase, use cursor incremental.
     * ```
     */
    override fun create(streamFeedBootstrap: StreamFeedBootstrap): MySqlSourceJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: DefaultJdbcStreamState = streamState(streamFeedBootstrap)

        // An empty table stream state will be marked as a nullNode. This prevents repeated attempt
        // to read it
        if (streamFeedBootstrap.currentState?.isNull == true) {
            return null
        }

        // A legacy saved state may be null for an empty table. We will attempt to read it again
        if (
            streamFeedBootstrap.currentState == null ||
                streamFeedBootstrap.currentState?.isEmpty == true
        ) {
            return coldStart(streamState)
        }

        val opaqueStateValue: OpaqueStateValue = streamFeedBootstrap.currentState!!

        val isCursorBased: Boolean = !sharedState.configuration.global

        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()

        if (
            pkChosenFromCatalog.isEmpty() &&
                stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH
        ) {
            if (
                streamState.streamFeedBootstrap.currentState ==
                    MySqlSourceJdbcStreamStateValue.snapshotCompleted
            ) {
                return null
            }
            return MySqlSourceJdbcNonResumableSnapshotPartition(
                selectQueryGenerator,
                streamState,
            )
        }

        if (!isCursorBased) {
            val sv: MySqlSourceCdcInitialSnapshotStateValue =
                Jsons.treeToValue(
                    opaqueStateValue,
                    MySqlSourceCdcInitialSnapshotStateValue::class.java
                )

            if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
                val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
                if (sv.pkVal == upperBound.asText()) {
                    return null
                }
                val pkLowerBound: JsonNode = stateValueToJsonNode(pkChosenFromCatalog[0], sv.pkVal)

                return MySqlSourceJdbcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = if (pkLowerBound.isNull) null else listOf(pkLowerBound),
                    upperBound = listOf(upperBound)
                )
            }

            if (sv.pkName == null) {
                // This indicates initial snapshot has been completed. CDC snapshot will be handled
                // by CDCPartitionFactory.
                // Nothing to do here.
                return null
            } else {
                // This branch indicates snapshot is incomplete. We need to resume based on previous
                // snapshot state.
                val pkField = pkChosenFromCatalog.first()
                val pkLowerBound: JsonNode = stateValueToJsonNode(pkField, sv.pkVal)

                if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
                    val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
                    if (sv.pkVal == upperBound.asText()) {
                        return null
                    }
                    return MySqlSourceJdbcCdcRfrSnapshotPartition(
                        selectQueryGenerator,
                        streamState,
                        pkChosenFromCatalog,
                        lowerBound = if (pkLowerBound.isNull) null else listOf(pkLowerBound),
                        upperBound = listOf(upperBound)
                    )
                }
                return MySqlSourceJdbcCdcSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = listOf(pkLowerBound),
                )
            }
        } else {
            val sv: MySqlSourceJdbcStreamStateValue =
                Jsons.treeToValue(opaqueStateValue, MySqlSourceJdbcStreamStateValue::class.java)

            if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
                val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
                if (sv.pkValue == upperBound.asText()) {
                    return null
                }
                val pkLowerBound: JsonNode =
                    stateValueToJsonNode(pkChosenFromCatalog[0], sv.pkValue)

                return MySqlSourceJdbcCdcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = if (pkLowerBound.isNull) null else listOf(pkLowerBound),
                    upperBound = listOf(upperBound)
                )
            }

            if (sv.stateType != "cursor_based") {
                // Loading value from catalog. Note there could be unexpected behaviors if user
                // updates their schema but did not reset their state.
                val pkField = pkChosenFromCatalog.first()
                val pkLowerBound: JsonNode = stateValueToJsonNode(pkField, sv.pkValue)

                val cursorChosenFromCatalog: Field =
                    stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

                // in a state where it's still in primary_key read part.
                return MySqlSourceJdbcSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = listOf(pkLowerBound),
                    cursorChosenFromCatalog,
                    cursorUpperBound = null,
                )
            }
            // resume back to cursor based increment.
            val cursor: Field = stream.fields.find { it.id == sv.cursorField.first() } as Field
            val cursorCheckpoint: JsonNode = stateValueToJsonNode(cursor, sv.cursors)

            // Compose a jsonnode of cursor label to cursor value to fit in
            // DefaultJdbcCursorIncrementalPartition
            if (cursorCheckpoint.isNull) {
                return coldStart(streamState)
            }

            if (cursorCheckpoint.toString() == streamState.cursorUpperBound?.toString()) {
                // Incremental complete.
                return null
            }
            return MySqlSourceJdbcCursorIncrementalPartition(
                selectQueryGenerator,
                streamState,
                cursor,
                cursorLowerBound = cursorCheckpoint,
                isLowerBoundIncluded = false,
                cursorUpperBound = streamState.cursorUpperBound,
            )
        }
    }

    // visible for testing
    fun stateValueToJsonNode(field: Field, stateValue: String?): JsonNode {
        when (field.type.airbyteSchemaType) {
            is LeafAirbyteSchemaType ->
                return when (field.type.airbyteSchemaType as LeafAirbyteSchemaType) {
                    LeafAirbyteSchemaType.INTEGER -> {
                        Jsons.valueToTree(stateValue?.toBigInteger())
                    }
                    LeafAirbyteSchemaType.NUMBER -> {
                        Jsons.valueToTree(stateValue?.toDouble())
                    }
                    LeafAirbyteSchemaType.BINARY -> {
                        try {
                            val ba = Base64.getDecoder().decode(stateValue!!)
                            Jsons.valueToTree<BinaryNode>(ba)
                        } catch (_: RuntimeException) {
                            Jsons.valueToTree<JsonNode>(stateValue)
                        }
                    }
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> {
                        val timestampInStatePattern = "yyyy-MM-dd'T'HH:mm:ss"
                        try {
                            val formatter: DateTimeFormatter =
                                DateTimeFormatterBuilder()
                                    .appendPattern(timestampInStatePattern)
                                    .optionalStart()
                                    .appendFraction(ChronoField.NANO_OF_SECOND, 1, 9, true)
                                    .optionalEnd()
                                    .toFormatter()

                            Jsons.textNode(
                                LocalDateTime.parse(stateValue, formatter)
                                    .format(LocalDateTimeCodec.formatter)
                            )
                        } catch (_: RuntimeException) {
                            // Resolve to use the new format.
                            Jsons.valueToTree<JsonNode>(stateValue)
                        }
                    }
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> {
                        val timestampInStatePattern = "yyyy-MM-dd'T'HH:mm:ss"
                        val formatter =
                            DateTimeFormatterBuilder()
                                .appendPattern(timestampInStatePattern)
                                .optionalStart()
                                .appendFraction(ChronoField.NANO_OF_SECOND, 1, 9, true)
                                .optionalEnd()
                                .optionalStart()
                                .optionalStart()
                                .appendLiteral(' ')
                                .optionalEnd()
                                .appendOffset("+HH:mm", "Z")
                                .optionalEnd()
                                .toFormatter()

                        try {
                            val offsetDateTime =
                                try {
                                    OffsetDateTime.parse(stateValue, formatter)
                                } catch (_: DateTimeParseException) {
                                    // if no offset exists, we assume it's UTC
                                    LocalDateTime.parse(stateValue, formatter).atOffset(UTC)
                                }
                            Jsons.valueToTree(offsetDateTime.format(OffsetDateTimeCodec.formatter))
                        } catch (_: RuntimeException) {
                            // Resolve to use the new format.
                            Jsons.valueToTree<JsonNode>(stateValue)
                        }
                    }
                    else -> Jsons.valueToTree<JsonNode>(stateValue)
                }
            else ->
                throw IllegalStateException(
                    "PK field must be leaf type but is ${field.type.airbyteSchemaType}."
                )
        }
    }

    override fun split(
        unsplitPartition: MySqlSourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<MySqlSourceJdbcPartition> {

        val stream: Stream = unsplitPartition.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: emptyList()

        if (pkChosenFromCatalog.isEmpty()) {
            return listOf(unsplitPartition)
        }

        val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
        log.info { "Found primary key upper bound: $upperBound" }

        val type = pkChosenFromCatalog[0].type as LosslessJdbcFieldType<*, *>
        val upperBoundVal = type.jsonDecoder.decode(upperBound)

        log.info { "Found primary key upper bound: $upperBoundVal" }

        return when (unsplitPartition) {
            is MySqlSourceJdbcSnapshotWithCursorPartition ->
                unsplitPartition.split(opaqueStateValues.size, upperBoundVal)
            is MySqlSourceJdbcRfrSnapshotPartition ->
                unsplitPartition.split(opaqueStateValues.size, upperBoundVal)
            is MySqlSourceJdbcCdcSnapshotPartition ->
                unsplitPartition.split(opaqueStateValues.size, upperBoundVal)
            else -> null
        }
            ?: listOf(unsplitPartition)
    }

    private fun MySqlSourceJdbcSnapshotWithCursorPartition.split(
        num: Int,
        upperBound: Any?
    ): List<MySqlSourceJdbcResumablePartition>? {
        val type = checkpointColumns[0].type as LosslessJdbcFieldType<*, *>
        val lowerBound =
            when (lowerBound.isNullOrEmpty()) {
                true -> null
                false -> type.jsonDecoder.decode(lowerBound[0])
            }
        return calculateBoundaries(num, lowerBound, upperBound)?.map { (l, u) ->
            MySqlSourceJdbcSplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                checkpointColumns,
                listOf(stateValueToJsonNode(checkpointColumns[0], l.toString())),
                listOf(stateValueToJsonNode(checkpointColumns[0], u.toString())),
                cursor,
                cursorUpperBound
            )
        }
    }

    private fun MySqlSourceJdbcRfrSnapshotPartition.split(
        num: Int,
        upperBound: Any?
    ): List<MySqlSourceJdbcResumablePartition>? {
        val type = checkpointColumns[0].type as LosslessJdbcFieldType<*, *>
        val lowerBound =
            when (lowerBound.isNullOrEmpty()) {
                true -> null
                false -> type.jsonDecoder.decode(lowerBound[0])
            }

        return calculateBoundaries(num, lowerBound, upperBound)?.map { (l, u) ->
            MySqlSourceJdbcSplittableRfrSnapshotPartition(
                selectQueryGenerator,
                streamState,
                checkpointColumns,
                listOf(stateValueToJsonNode(checkpointColumns[0], l.toString())),
                listOf(stateValueToJsonNode(checkpointColumns[0], u.toString())),
            )
        }
    }

    private fun MySqlSourceJdbcCdcSnapshotPartition.split(
        num: Int,
        upperBound: Any?
    ): List<MySqlSourceJdbcResumablePartition>? {
        val type = checkpointColumns[0].type as LosslessJdbcFieldType<*, *>
        val lowerBound =
            when (lowerBound.isNullOrEmpty()) {
                true -> null
                false -> type.jsonDecoder.decode(lowerBound[0])
            }

        return calculateBoundaries(num, lowerBound, upperBound)?.map { (l, u) ->
            MySqlSourceJdbcSplittableCdcRfrSnapshotPartition(
                selectQueryGenerator,
                streamState,
                checkpointColumns,
                listOf(stateValueToJsonNode(checkpointColumns[0], l.toString())),
                listOf(stateValueToJsonNode(checkpointColumns[0], u.toString())),
            )
        }
    }

    private fun <T> calculateBoundaries(num: Int, lowerBound: T?, upperBound: T): Map<*, *>? {
        return when (upperBound) {
            is Long -> calculateBoundaries(num, lowerBound as Long?, upperBound)
            is String -> calculateBoundaries(num, lowerBound as String?, upperBound)
            is Double -> calculateBoundaries(num, lowerBound as Double?, upperBound)
            else -> null
        }
    }
    private fun calculateBoundaries(
        num: Int,
        lowerBound: Long?,
        upperBound: Long
    ): Map<Long, Long> {
        var queryPlan: MutableList<Long> = mutableListOf()
        val effectiveLowerBound = lowerBound ?: 0L
        val eachStep: Long = (upperBound - effectiveLowerBound) / num
        for (i in 1..(num - 1)) {
            queryPlan.add(i * eachStep)
        }

        val lbs: List<Long> = listOf(effectiveLowerBound) + queryPlan
        val ubs: List<Long> = queryPlan + upperBound
        return lbs.zip(ubs).toMap()
    }

    private fun calculateBoundaries(
        num: Int,
        lowerBound: Double?,
        upperBound: Double
    ): Map<Double, Double> {
        var queryPlan: MutableList<Double> = mutableListOf()
        val effectiveLowerBound = lowerBound ?: 0.0
        val eachStep: Double = (upperBound - effectiveLowerBound) / num
        for (i in 1..(num - 1)) {
            queryPlan.add(i * eachStep)
        }
        val lbs: List<Double> = listOf(effectiveLowerBound) + queryPlan
        val ubs: List<Double> = queryPlan + upperBound
        return lbs.zip(ubs).toMap()
    }

    private fun calculateBoundaries(
        num: Int,
        lowerBound: String?,
        upperBound: String
    ): Map<String, String> {
        val effectiveLowerBound = lowerBound ?: String()
        var queryPlan: List<String> =
            unicodeInterpolatedStrings(effectiveLowerBound, upperBound, num)
        val lbs: List<String> = listOf(effectiveLowerBound) + queryPlan
        val ubs: List<String> = queryPlan + upperBound
        return lbs.zip(ubs).toMap()
    }

    fun unicodeInterpolatedStrings(start: String, end: String, steps: Int): List<String> {
        fun toCodePoints(s: String): List<Int> {
            val codePoints = mutableListOf<Int>()
            var i = 0
            while (i < s.length) {
                val cp = s.codePointAt(i)
                codePoints.add(cp)
                i += Character.charCount(cp)
            }
            return codePoints
        }

        fun fromCodePoints(codePoints: List<Int>): String {
            val sb = StringBuilder()
            for (cp in codePoints) {
                sb.append(Character.toChars(cp))
            }
            return sb.toString()
        }

        fun codePointsToBigInt(cps: List<Int>, base: BigInteger): BigInteger {
            var result = BigInteger.ZERO
            for (cp in cps) {
                result = result.multiply(base).add(BigInteger.valueOf(cp.toLong()))
            }
            return result
        }

        fun bigIntToCodePoints(num: BigInteger, length: Int, base: BigInteger): List<Int> {
            var n = num
            val result = MutableList(length) { 0 }
            for (i in (length - 1) downTo 0) {
                val rem = n.mod(base).toInt()
                result[i] = rem
                n = n.divide(base)
            }
            return result
        }

        val base = BigInteger.valueOf(0x110000L) // Max Unicode code point + 1
        val a = toCodePoints(start)
        val b = toCodePoints(end)
        val maxLen = maxOf(a.size, b.size)
        val aPadded = a + List(maxLen - a.size) { 0 }
        val bPadded = b + List(maxLen - b.size) { 0 }

        val aNum = codePointsToBigInt(aPadded, base)
        val bNum = codePointsToBigInt(bPadded, base)

        val result = mutableListOf<String>()
        for (i in 0..steps) {
            val fraction =
                BigInteger.valueOf(i.toLong())
                    .multiply(bNum - aNum)
                    .divide(BigInteger.valueOf(steps.toLong()))
            val mid = aNum + fraction
            val cps = bigIntToCodePoints(mid, maxLen, base)
            result.add(fromCodePoints(cps))
        }

        return result
    }
}
