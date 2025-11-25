/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.BinaryNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.Equal
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.FromSample
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.GreaterOrEqual
import io.airbyte.cdk.read.JdbcCursorPartition
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcSplittablePartition
import io.airbyte.cdk.read.Lesser
import io.airbyte.cdk.read.LesserOrEqual
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.NoWhere
import io.airbyte.cdk.read.Or
import io.airbyte.cdk.read.OrderBy
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.WhereClauseLeafNode
import io.airbyte.cdk.read.WhereClauseNode
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeParseException
import java.util.Base64

private val log = KotlinLogging.logger {}

/**
 * Determines the effective cursor checkpoint value by comparing cursor cutoff time with upper
 * bound. Returns cutoff time if it's less than upper bound, otherwise returns upper bound (or
 * fallback if null).
 */
private fun getEffectiveCursorCheckpoint(
    cursorCutoffTime: JsonNode?,
    cursorUpperBound: JsonNode?,
    fallback: JsonNode
): JsonNode {
    return if (
        cursorCutoffTime != null &&
            !cursorCutoffTime.isNull &&
            cursorUpperBound != null &&
            !cursorUpperBound.isNull &&
            cursorCutoffTime.asText() < cursorUpperBound.asText()
    ) {
        cursorCutoffTime
    } else {
        cursorUpperBound ?: fallback
    }
}

/**
 * Converts a state value string to a JsonNode based on the field type. This function handles type
 * conversions and date formatting for state checkpoints.
 */
fun stateValueToJsonNode(field: Field, stateValue: String?): JsonNode {
    when (field.type.airbyteSchemaType) {
        is LeafAirbyteSchemaType ->
            return when (field.type.airbyteSchemaType as LeafAirbyteSchemaType) {
                LeafAirbyteSchemaType.INTEGER -> {
                    Jsons.valueToTree(
                        stateValue?.takeIf { it.isNotEmpty() && it != "null" }?.toBigInteger()
                    )
                }
                LeafAirbyteSchemaType.NUMBER -> {
                    Jsons.valueToTree(
                        stateValue?.takeIf { it.isNotEmpty() && it != "null" }?.toBigDecimal()
                    )
                }
                LeafAirbyteSchemaType.BINARY -> {
                    val ba = Base64.getDecoder().decode(stateValue!!)
                    Jsons.valueToTree<BinaryNode>(ba)
                }
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> {
                    try {
                        val parsedDate =
                            LocalDateTime.parse(
                                stateValue,
                                MsSqlServerJdbcPartitionFactory.inputDateFormatter
                            )
                        val dateAsString =
                            parsedDate.format(MsSqlServerJdbcPartitionFactory.outputDateFormatter)
                        Jsons.textNode(dateAsString)
                    } catch (e: DateTimeParseException) {
                        // Resolve to use the new format.
                        Jsons.valueToTree(stateValue)
                    }
                }
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> {
                    try {
                        if (stateValue == null || stateValue.isEmpty()) {
                            return Jsons.nullNode()
                        }

                        // Normalize: remove spaces before timezone indicators
                        val normalizedValue =
                            stateValue.trim().replace(Regex("\\s+(?=[+\\-]|Z)"), "")

                        // Try parsing with timezone first, then fall back to assuming UTC
                        val offsetDateTime =
                            try {
                                OffsetDateTime.parse(
                                    normalizedValue,
                                    MsSqlServerJdbcPartitionFactory.timestampWithTimezoneParser
                                )
                            } catch (e: DateTimeParseException) {
                                // No timezone info - parse as LocalDateTime and assume UTC
                                LocalDateTime.parse(
                                        normalizedValue,
                                        MsSqlServerJdbcPartitionFactory
                                            .timestampWithoutTimezoneParser
                                    )
                                    .atOffset(ZoneOffset.UTC)
                            }

                        // Format using standard codec formatter (6 decimal places, Z or offset)
                        Jsons.valueToTree(offsetDateTime.format(OffsetDateTimeCodec.formatter))
                    } catch (e: DateTimeParseException) {
                        // If all parsing fails, return as-is (already in new format)
                        Jsons.valueToTree(stateValue)
                    }
                }
                else -> Jsons.valueToTree(stateValue)
            }
        else ->
            throw IllegalStateException(
                "PK field must be leaf type but is ${field.type.airbyteSchemaType}."
            )
    }
}

sealed class MsSqlServerJdbcPartition(
    val selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
) : JdbcPartition<DefaultJdbcStreamState> {
    val stream: Stream = streamState.stream
    val from = From(stream.name, stream.namespace)

    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    open val nonResumableQuerySpec = SelectQuerySpec(SelectColumns(stream.fields), from)

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns(stream.fields),
                From(stream.name, stream.namespace),
                limit = Limit(sampleSize.toLong()),
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }
}

class MsSqlServerJdbcNonResumableSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
) : MsSqlServerJdbcPartition(selectQueryGenerator, streamState) {

    override val completeState: OpaqueStateValue = MsSqlServerJdbcStreamStateValue.snapshotCompleted
}

class MsSqlServerJdbcNonResumableSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    val cursor: Field,
    val cursorCutoffTime: JsonNode? = null,
) :
    MsSqlServerJdbcPartition(selectQueryGenerator, streamState),
    JdbcCursorPartition<DefaultJdbcStreamState> {

    override val completeState: OpaqueStateValue
        get() =
            MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                cursorCheckpoint = streamState.cursorUpperBound ?: Jsons.nullNode(),
            )

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec: SelectQuerySpec
        get() =
            if (cursorCutoffTime != null) {
                // When excluding today's data, apply cutoff constraint to upper bound query too
                SelectQuerySpec(
                    SelectColumnMaxValue(cursor),
                    from,
                    Where(Lesser(cursor, cursorCutoffTime))
                )
            } else {
                SelectQuerySpec(SelectColumnMaxValue(cursor), from)
            }

    override val nonResumableQuerySpec: SelectQuerySpec
        get() {
            // Add cutoff time constraint if present
            return if (cursorCutoffTime != null) {
                SelectQuerySpec(
                    SelectColumns(stream.fields),
                    from,
                    Where(Lesser(cursor, cursorCutoffTime))
                )
            } else {
                SelectQuerySpec(SelectColumns(stream.fields), from)
            }
        }
}

sealed class MsSqlServerJdbcResumablePartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    val checkpointColumns: List<Field>,
) :
    MsSqlServerJdbcPartition(selectQueryGenerator, streamState),
    JdbcSplittablePartition<DefaultJdbcStreamState> {
    abstract val lowerBound: List<JsonNode>?
    abstract val upperBound: List<JsonNode>?

    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    override val nonResumableQuerySpec: SelectQuerySpec
        get() = SelectQuerySpec(SelectColumns(stream.fields), from, where)

    override fun resumableQuery(limit: Long): SelectQuery {
        val querySpec =
            SelectQuerySpec(
                SelectColumns((stream.fields + checkpointColumns).distinct()),
                from,
                where,
                OrderBy(checkpointColumns),
                Limit(limit),
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns(stream.fields + checkpointColumns),
                FromSample(stream.name, stream.namespace, sampleRateInvPow2, sampleSize),
                NoWhere,
                OrderBy(checkpointColumns),
                Limit(sampleSize.toLong())
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    val where: Where
        get() {
            val zippedLowerBound: List<Pair<Field, JsonNode>> =
                lowerBound?.let { checkpointColumns.zip(it) } ?: listOf()
            val lowerBoundDisj: List<WhereClauseNode> =
                zippedLowerBound.mapIndexed { idx: Int, (gtCol: Field, gtValue: JsonNode) ->
                    val lastLeaf: WhereClauseLeafNode =
                        if (isLowerBoundIncluded && idx == checkpointColumns.size - 1) {
                            GreaterOrEqual(gtCol, gtValue)
                        } else {
                            Greater(gtCol, gtValue)
                        }
                    And(
                        zippedLowerBound.take(idx).map { (eqCol: Field, eqValue: JsonNode) ->
                            Equal(eqCol, eqValue)
                        } + listOf(lastLeaf),
                    )
                }
            val zippedUpperBound: List<Pair<Field, JsonNode>> =
                upperBound?.let { checkpointColumns.zip(it) } ?: listOf()
            val upperBoundDisj: List<WhereClauseNode> =
                zippedUpperBound.mapIndexed { idx: Int, (leqCol: Field, leqValue: JsonNode) ->
                    val lastLeaf: WhereClauseLeafNode =
                        if (idx < zippedUpperBound.size - 1) {
                            Lesser(leqCol, leqValue)
                        } else {
                            LesserOrEqual(leqCol, leqValue)
                        }
                    And(
                        zippedUpperBound.take(idx).map { (eqCol: Field, eqValue: JsonNode) ->
                            Equal(eqCol, eqValue)
                        } + listOf(lastLeaf),
                    )
                }
            val baseClause = And(Or(lowerBoundDisj), Or(upperBoundDisj))
            // Add additional where clause if present
            val additional = additionalWhereClause
            return if (additional != null) {
                Where(And(baseClause, additional))
            } else {
                Where(baseClause)
            }
        }

    open val isLowerBoundIncluded: Boolean = false

    open val additionalWhereClause: WhereClauseNode? = null
}

/** RFR for cursor based read. */
class MsSqlServerJdbcRfrSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
) : MsSqlServerJdbcResumablePartition(selectQueryGenerator, streamState, primaryKey) {

    // TODO: this needs to reflect lastRecord. Complete state needs to have last primary key value
    // in RFR case.
    override val completeState: OpaqueStateValue
        get() =
            when (upperBound) {
                null -> MsSqlServerJdbcStreamStateValue.snapshotCompleted
                else ->
                    MsSqlServerJdbcStreamStateValue.snapshotCheckpoint(
                        primaryKey = checkpointColumns,
                        primaryKeyCheckpoint = upperBound,
                    )
            }

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerJdbcStreamStateValue.snapshotCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
        )
}

/** RFR for CDC. */
class MsSqlServerJdbcCdcRfrSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
) : MsSqlServerJdbcResumablePartition(selectQueryGenerator, streamState, primaryKey) {
    override val completeState: OpaqueStateValue
        get() =
            when (upperBound) {
                null -> MsSqlServerCdcInitialSnapshotStateValue.getSnapshotCompletedState(stream)
                else ->
                    MsSqlServerCdcInitialSnapshotStateValue.snapshotCheckpoint(
                        primaryKey = checkpointColumns,
                        primaryKeyCheckpoint = upperBound,
                    )
            }

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerCdcInitialSnapshotStateValue.snapshotCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
        )
}

/**
 * Implementation of a [JdbcPartition] for a CDC snapshot partition. Used for incremental CDC
 * initial sync.
 */
class MsSqlServerJdbcCdcSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
) : MsSqlServerJdbcResumablePartition(selectQueryGenerator, streamState, primaryKey) {
    override val upperBound: List<JsonNode>? = null
    override val completeState: OpaqueStateValue
        get() = MsSqlServerCdcInitialSnapshotStateValue.getSnapshotCompletedState(stream)

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerCdcInitialSnapshotStateValue.snapshotCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
        )
}

sealed class MsSqlServerJdbcCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    checkpointColumns: List<Field>,
    val cursor: Field,
    private val explicitCursorUpperBound: JsonNode?,
    val cursorCutoffTime: JsonNode? = null,
) :
    MsSqlServerJdbcResumablePartition(selectQueryGenerator, streamState, checkpointColumns),
    JdbcCursorPartition<DefaultJdbcStreamState> {

    val cursorUpperBound: JsonNode?
        get() = explicitCursorUpperBound ?: streamState.cursorUpperBound

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec: SelectQuerySpec
        get() =
            if (cursorCutoffTime != null) {
                // When excluding today's data, apply cutoff constraint to upper bound query too
                SelectQuerySpec(
                    SelectColumnMaxValue(cursor),
                    from,
                    Where(Lesser(cursor, cursorCutoffTime))
                )
            } else {
                SelectQuerySpec(SelectColumnMaxValue(cursor), from)
            }

    // Override samplingQuery to avoid TABLESAMPLE for cursor-based operations
    // TABLESAMPLE fails on views and isn't needed for cursor-based incremental reads
    // which are typically small (only new/changed data)
    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns(stream.fields + checkpointColumns),
                from,
                NoWhere,
                OrderBy(checkpointColumns),
                Limit(sampleSize.toLong())
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    override val additionalWhereClause: WhereClauseNode?
        get() =
            if (cursorCutoffTime != null) {
                // Add an additional constraint for the cutoff time
                Lesser(cursor, cursorCutoffTime)
            } else {
                null
            }
}

class MsSqlServerJdbcSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
    cursor: Field,
    cursorUpperBound: JsonNode?,
    cursorCutoffTime: JsonNode? = null,
) :
    MsSqlServerJdbcCursorPartition(
        selectQueryGenerator,
        streamState,
        primaryKey,
        cursor,
        cursorUpperBound,
        cursorCutoffTime
    ) {
    // UpperBound is always null for the initial partition that gets split
    override val upperBound: List<JsonNode>? = null

    override val completeState: OpaqueStateValue
        get() =
            MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                getEffectiveCursorCheckpoint(cursorCutoffTime, cursorUpperBound, Jsons.nullNode()),
            )

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerJdbcStreamStateValue.snapshotWithCursorCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
            cursor,
        )
}

class MsSqlServerJdbcSplittableSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
    cursor: Field,
    cursorUpperBound: JsonNode?,
    cursorCutoffTime: JsonNode? = null,
) :
    MsSqlServerJdbcCursorPartition(
        selectQueryGenerator,
        streamState,
        primaryKey,
        cursor,
        cursorUpperBound,
        cursorCutoffTime
    ) {
    override val completeState: OpaqueStateValue
        get() =
            when (upperBound) {
                null ->
                    MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
                        cursor,
                        getEffectiveCursorCheckpoint(
                            cursorCutoffTime,
                            cursorUpperBound,
                            Jsons.nullNode()
                        ),
                    )
                else ->
                    MsSqlServerJdbcStreamStateValue.snapshotWithCursorCheckpoint(
                        primaryKey = checkpointColumns,
                        primaryKeyCheckpoint = upperBound,
                        cursor,
                    )
            }

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerJdbcStreamStateValue.snapshotWithCursorCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
            cursor,
        )
}

/**
 * Default implementation of a [JdbcPartition] for a cursor incremental partition. These are always
 * splittable.
 */
class MsSqlServerJdbcCursorIncrementalPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    cursor: Field,
    val cursorLowerBound: JsonNode,
    override val isLowerBoundIncluded: Boolean,
    cursorUpperBound: JsonNode?,
    cursorCutoffTime: JsonNode? = null,
) :
    MsSqlServerJdbcCursorPartition(
        selectQueryGenerator,
        streamState,
        listOf(cursor),
        cursor,
        cursorUpperBound,
        cursorCutoffTime
    ) {
    override val lowerBound: List<JsonNode> = listOf(cursorLowerBound)
    override val upperBound: List<JsonNode>?
        get() = cursorUpperBound?.let { listOf(it) }

    override val completeState: OpaqueStateValue
        get() =
            MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                getEffectiveCursorCheckpoint(cursorCutoffTime, cursorUpperBound, cursorLowerBound),
            )

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
            cursor,
            cursorCheckpoint = lastRecord[cursor.id] ?: Jsons.nullNode(),
        )
}

// Extension methods for splitting MSSQL partitions
fun MsSqlServerJdbcRfrSnapshotPartition.split(
    opaqueStateValues: List<OpaqueStateValue>
): List<MsSqlServerJdbcRfrSnapshotPartition> {
    val splitPointValues: List<MsSqlServerJdbcStreamStateValue> =
        opaqueStateValues.map { MsSqlServerStateMigration.parseStateValue(it) }

    val inners: List<List<JsonNode>> =
        splitPointValues.mapNotNull { sv ->
            if (sv.pkValue != null) {
                listOf(sv.pkValue)
            } else null
        }

    val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
    val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)

    return lbs.zip(ubs).map { (lowerBound, upperBound) ->
        MsSqlServerJdbcRfrSnapshotPartition(
            selectQueryGenerator,
            streamState,
            checkpointColumns,
            lowerBound,
            upperBound,
        )
    }
}

fun MsSqlServerJdbcCdcRfrSnapshotPartition.split(
    opaqueStateValues: List<OpaqueStateValue>
): List<MsSqlServerJdbcCdcRfrSnapshotPartition> {
    val splitPointValues: List<MsSqlServerCdcInitialSnapshotStateValue> =
        opaqueStateValues.map {
            Jsons.treeToValue(it, MsSqlServerCdcInitialSnapshotStateValue::class.java)
        }

    val inners: List<List<JsonNode>> =
        splitPointValues.mapNotNull { sv ->
            val pkField = checkpointColumns.firstOrNull()
            if (pkField != null && sv.pkVal != null) {
                listOf(stateValueToJsonNode(pkField, sv.pkVal))
            } else null
        }

    val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
    val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)

    return lbs.zip(ubs).map { (lowerBound, upperBound) ->
        MsSqlServerJdbcCdcRfrSnapshotPartition(
            selectQueryGenerator,
            streamState,
            checkpointColumns,
            lowerBound,
            upperBound,
        )
    }
}

fun MsSqlServerJdbcCdcSnapshotPartition.split(
    opaqueStateValues: List<OpaqueStateValue>
): List<MsSqlServerJdbcCdcRfrSnapshotPartition> {
    val splitPointValues: List<MsSqlServerCdcInitialSnapshotStateValue> =
        opaqueStateValues.map {
            Jsons.treeToValue(it, MsSqlServerCdcInitialSnapshotStateValue::class.java)
        }

    val inners: List<List<JsonNode>> =
        splitPointValues.mapNotNull { sv ->
            val pkField = checkpointColumns.firstOrNull()
            if (pkField != null && sv.pkVal != null) {
                listOf(stateValueToJsonNode(pkField, sv.pkVal))
            } else null
        }

    val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
    val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)

    return lbs.zip(ubs).map { (lowerBound, upperBound) ->
        MsSqlServerJdbcCdcRfrSnapshotPartition(
            selectQueryGenerator,
            streamState,
            checkpointColumns,
            lowerBound,
            upperBound,
        )
    }
}

fun MsSqlServerJdbcSnapshotWithCursorPartition.split(
    opaqueStateValues: List<OpaqueStateValue>
): List<MsSqlServerJdbcSplittableSnapshotWithCursorPartition> {
    val splitPointValues: List<MsSqlServerJdbcStreamStateValue> =
        opaqueStateValues.map { MsSqlServerStateMigration.parseStateValue(it) }

    val inners: List<List<JsonNode>> =
        splitPointValues.mapNotNull { sv ->
            if (sv.pkValue != null) {
                listOf(sv.pkValue)
            } else null
        }

    val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
    val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)

    return lbs.zip(ubs).map { (lowerBound, upperBound) ->
        MsSqlServerJdbcSplittableSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            checkpointColumns,
            lowerBound,
            upperBound,
            cursor,
            cursorUpperBound,
            cursorCutoffTime,
        )
    }
}
