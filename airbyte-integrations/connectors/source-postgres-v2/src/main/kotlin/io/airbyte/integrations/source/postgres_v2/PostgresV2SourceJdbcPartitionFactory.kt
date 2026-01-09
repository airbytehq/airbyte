/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

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
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset.UTC
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.DateTimeParseException
import java.time.temporal.ChronoField
import java.util.Base64
import java.util.concurrent.ConcurrentHashMap

@Primary
@Singleton
class PostgresV2SourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: PostgresV2SourceOperations,
    val config: PostgresV2SourceConfiguration,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        PostgresV2SourceJdbcPartition,
    > {

    private val log = KotlinLogging.logger {}
    private val streamStates = ConcurrentHashMap<StreamIdentifier, DefaultJdbcStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DefaultJdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            DefaultJdbcStreamState(sharedState, streamFeedBootstrap)
        }

    private fun findPkUpperBound(stream: Stream, pkChosenFromCatalog: List<Field>): JsonNode {
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
                return Jsons.nullNode()
            }
        }
    }

    private fun findPkLowerBound(stream: Stream, pkChosenFromCatalog: List<Field>): JsonNode {
        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        val from = From(stream.name, stream.namespace)
        jdbcConnectionFactory.get().use { connection ->
            val sql =
                "SELECT MIN(\"${pkChosenFromCatalog.first().id}\") ${
                    if (from.namespace == null) "FROM \"${from.name}\"" else "FROM \"${from.namespace}\".\"${from.name}\""
                }"
            val stmt = connection.prepareStatement(sql)
            val rs = stmt.executeQuery()

            if (rs.next()) {
                val jdbcFieldType = pkChosenFromCatalog[0].type as JdbcFieldType<*>
                val pkLowerBound: JsonNode = jdbcFieldType.get(rs, 1)
                return pkLowerBound
            } else {
                return Jsons.nullNode()
            }
        }
    }

    private fun coldStart(streamState: DefaultJdbcStreamState): PostgresV2SourceJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()

        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            if (pkChosenFromCatalog.isEmpty()) {
                return PostgresV2SourceJdbcNonResumableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }

            val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
            return PostgresV2SourceJdbcRfrSnapshotPartition(
                selectQueryGenerator,
                streamState,
                pkChosenFromCatalog,
                lowerBound = null,
                upperBound = listOf(upperBound)
            )
        }

        val cursorChosenFromCatalog: Field =
            stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

        if (pkChosenFromCatalog.isEmpty()) {
            return PostgresV2SourceJdbcNonResumableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog
            )
        }
        return PostgresV2SourceJdbcSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            pkChosenFromCatalog,
            lowerBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )
    }

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): PostgresV2SourceJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: DefaultJdbcStreamState = streamState(streamFeedBootstrap)

        // An empty table stream state will be marked as a nullNode
        if (streamFeedBootstrap.currentState?.isNull == true) {
            return null
        }

        // Cold start if no state
        if (
            streamFeedBootstrap.currentState == null ||
                streamFeedBootstrap.currentState?.isEmpty == true
        ) {
            return coldStart(streamState)
        }

        val opaqueStateValue: OpaqueStateValue = streamFeedBootstrap.currentState!!

        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()

        if (
            pkChosenFromCatalog.isEmpty() &&
                stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH
        ) {
            if (
                streamState.streamFeedBootstrap.currentState ==
                    PostgresV2SourceJdbcStreamStateValue.snapshotCompleted
            ) {
                return null
            }
            return PostgresV2SourceJdbcNonResumableSnapshotPartition(
                selectQueryGenerator,
                streamState,
            )
        }

        val sv: PostgresV2SourceJdbcStreamStateValue =
            Jsons.treeToValue(opaqueStateValue, PostgresV2SourceJdbcStreamStateValue::class.java)

        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
            if (sv.pkValue == upperBound.asText() || sv.pkValue == null) {
                return null
            }
            val pkLowerBound: JsonNode = stateValueToJsonNode(pkChosenFromCatalog[0], sv.pkValue)

            return PostgresV2SourceJdbcRfrSnapshotPartition(
                selectQueryGenerator,
                streamState,
                pkChosenFromCatalog,
                lowerBound = if (pkLowerBound.isNull) null else listOf(pkLowerBound),
                upperBound = listOf(upperBound)
            )
        }

        // Cursor-based incremental
        if (sv.stateType != "cursor_based") {
            // Still in primary_key read phase
            val pkField = pkChosenFromCatalog.first()
            val pkLowerBound: JsonNode = stateValueToJsonNode(pkField, sv.pkValue)

            val cursorChosenFromCatalog: Field =
                stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

            return PostgresV2SourceJdbcSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                pkChosenFromCatalog,
                lowerBound = listOf(pkLowerBound),
                cursorChosenFromCatalog,
                cursorUpperBound = null,
            )
        }

        // Resume cursor based incremental
        val cursor: Field = stream.fields.find { it.id == sv.cursorField.first() } as Field
        val cursorCheckpoint: JsonNode = stateValueToJsonNode(cursor, sv.cursors)

        if (cursorCheckpoint.isNull) {
            return coldStart(streamState)
        }

        if (cursorCheckpoint.toString() == streamState.cursorUpperBound?.toString()) {
            return null
        }

        return PostgresV2SourceJdbcCursorIncrementalPartition(
            selectQueryGenerator,
            streamState,
            cursor,
            cursorLowerBound = cursorCheckpoint,
            isLowerBoundIncluded = false,
            cursorUpperBound = streamState.cursorUpperBound,
        )
    }

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
                                    LocalDateTime.parse(stateValue, formatter).atOffset(UTC)
                                }
                            Jsons.valueToTree(offsetDateTime.format(OffsetDateTimeCodec.formatter))
                        } catch (_: RuntimeException) {
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
        unsplitPartition: PostgresV2SourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<PostgresV2SourceJdbcPartition> {

        val stream: Stream = unsplitPartition.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: emptyList()

        if (pkChosenFromCatalog.isEmpty()) {
            return listOf(unsplitPartition)
        }

        val pkType = pkChosenFromCatalog[0].type as LosslessJdbcFieldType<*, *>
        val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
        val upperBoundVal = pkType.jsonDecoder.decode(upperBound)
        log.info { "Found primary key upper bound: $upperBoundVal" }

        val lowerBound = findPkLowerBound(stream, pkChosenFromCatalog)
        val lowerBoundVal = pkType.jsonDecoder.decode(lowerBound)
        log.info { "Found primary key lower bound: $lowerBoundVal" }

        return when (unsplitPartition) {
            is PostgresV2SourceJdbcSnapshotWithCursorPartition ->
                unsplitPartition.split(opaqueStateValues, upperBoundVal, lowerBoundVal)
            is PostgresV2SourceJdbcRfrSnapshotPartition ->
                unsplitPartition.split(opaqueStateValues, upperBoundVal, lowerBoundVal)
            else -> null
        }
            ?: listOf(unsplitPartition)
    }

    private fun PostgresV2SourceJdbcSnapshotWithCursorPartition.split(
        opaqueStateValues: List<OpaqueStateValue>,
        upperBound: Any?,
        effectiveLowerBound: Any?,
    ): List<PostgresV2SourceJdbcResumablePartition>? {
        val type = checkpointColumns[0].type as LosslessJdbcFieldType<*, *>
        val lowerBound =
            when (lowerBound.isNullOrEmpty()) {
                true -> effectiveLowerBound
                false -> type.jsonDecoder.decode(lowerBound[0])
            }
        return calculateBoundaries(opaqueStateValues, lowerBound, upperBound)
            ?.entries
            ?.mapIndexed { index, (l, u) ->
                PostgresV2SourceJdbcSplittableSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    checkpointColumns,
                    listOf(stateValueToJsonNode(checkpointColumns[0], l.toString())),
                    u?.let { listOf(stateValueToJsonNode(checkpointColumns[0], u.toString())) },
                    cursor,
                    cursorUpperBound,
                    index == 0
                )
            }
    }

    private fun PostgresV2SourceJdbcRfrSnapshotPartition.split(
        opaqueStateValues: List<OpaqueStateValue>,
        upperBound: Any?,
        effectiveLowerBound: Any?,
    ): List<PostgresV2SourceJdbcResumablePartition>? {
        val type = checkpointColumns[0].type as LosslessJdbcFieldType<*, *>
        val lowerBound =
            when (lowerBound.isNullOrEmpty()) {
                true -> effectiveLowerBound
                false -> type.jsonDecoder.decode(lowerBound[0])
            }

        return calculateBoundaries(opaqueStateValues, lowerBound, upperBound)?.map { (l, u) ->
            PostgresV2SourceJdbcSplittableRfrSnapshotPartition(
                selectQueryGenerator,
                streamState,
                checkpointColumns,
                listOf(stateValueToJsonNode(checkpointColumns[0], l.toString())),
                u?.let { listOf(stateValueToJsonNode(checkpointColumns[0], u.toString())) },
            )
        }
    }

    private fun <T> calculateBoundaries(
        opaqueStateValues: List<OpaqueStateValue>,
        lowerBound: T?,
        upperBound: T
    ): Map<*, *>? =
        when {
            lowerBound is Long? && upperBound is Long ->
                internalCalculateBoundaries(opaqueStateValues, lowerBound, upperBound)
            lowerBound is Int? && upperBound is Int ->
                internalCalculateBoundaries(
                    opaqueStateValues,
                    lowerBound?.toLong(),
                    upperBound.toLong()
                )
            lowerBound is String? && upperBound is String ->
                internalCalculateBoundaries(opaqueStateValues, lowerBound, upperBound)
            lowerBound is Double? && upperBound is Double ->
                internalCalculateBoundaries(opaqueStateValues, lowerBound, upperBound)
            else -> null
        }

    private fun internalCalculateBoundaries(
        opaqueStateValues: List<OpaqueStateValue>,
        lowerBound: Long?,
        upperBound: Long
    ): Map<Long, Long?> {
        val num = opaqueStateValues.size
        val queryPlan: MutableList<Long> = mutableListOf()
        val effectiveLowerBound = lowerBound ?: Long.MIN_VALUE
        val eachStep: Long = (upperBound - effectiveLowerBound) / num
        for (i in 1..(num - 1)) {
            queryPlan.add(effectiveLowerBound + i * eachStep)
        }

        val lbs: List<Long> = listOf(effectiveLowerBound) + queryPlan
        val ubs: List<Long?> = queryPlan + null
        log.info { "partitions: ${lbs.zip(ubs)}" }
        return lbs.zip(ubs).toMap()
    }

    private fun internalCalculateBoundaries(
        opaqueStateValues: List<OpaqueStateValue>,
        lowerBound: Double?,
        upperBound: Double
    ): Map<Double, Double?> {
        val num = opaqueStateValues.size
        val queryPlan: MutableList<Double> = mutableListOf()
        val effectiveLowerBound = lowerBound ?: Double.MIN_VALUE
        val eachStep: Double = (upperBound - effectiveLowerBound) / num
        for (i in 1..(num - 1)) {
            queryPlan.add(effectiveLowerBound + i * eachStep)
        }
        val lbs: List<Double> = listOf(effectiveLowerBound) + queryPlan
        val ubs: List<Double?> = queryPlan + null
        return lbs.zip(ubs).toMap()
    }

    private fun internalCalculateBoundaries(
        opaqueStateValues: List<OpaqueStateValue>,
        lowerBound: String?,
        upperBound: String,
    ): Map<String, String?> {
        // opaqueStateValues.size could be used for more sophisticated boundary calculation
        val effectiveLowerBound = lowerBound ?: String()
        log.info { "calculating boundaries: [$effectiveLowerBound], [$upperBound]" }

        // For now, simple boundary calculation for strings
        val lbs: List<String> = listOf(effectiveLowerBound)
        val ubs: List<String?> = listOf(null)
        return lbs.zip(ubs).toMap()
    }
}
