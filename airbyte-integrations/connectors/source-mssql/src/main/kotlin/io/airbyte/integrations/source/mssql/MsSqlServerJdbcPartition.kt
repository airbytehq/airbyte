/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
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

private val log = KotlinLogging.logger {}
/** Base class for default implementations of [JdbcPartition] for non resumable partitions. */
sealed class MsSqlServerJdbcPartition(
    val selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
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

/** Default implementation of a [JdbcPartition] for an unsplittable snapshot partition. */
class MsSqlServerJdbcNonResumableSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
) : MsSqlServerJdbcPartition(selectQueryGenerator, streamState) {

    override val completeState: OpaqueStateValue = MsSqlServerJdbcStreamStateValue.snapshotCompleted
}

/**
 * Default implementation of a [JdbcPartition] for an non resumable snapshot partition preceding a
 * cursor-based incremental sync.
 */
class MsSqlServerJdbcNonResumableSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
    val cursor: Field,
) :
    MsSqlServerJdbcPartition(selectQueryGenerator, streamState),
    JdbcCursorPartition<DefaultJdbcStreamState> {

    override val completeState: OpaqueStateValue
        get() =
            MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                cursorCheckpoint = streamState.cursorUpperBound!!,
                streamState.stream,
            )

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec = SelectQuerySpec(SelectColumnMaxValue(cursor), from)
}

/** Base class for default implementations of [JdbcPartition] for partitions. */
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
            return Where(And(Or(lowerBoundDisj), Or(upperBoundDisj)))
        }

    open val isLowerBoundIncluded: Boolean = false
}

/** RFR for cursor based read. */
class MsSqlServerJdbcRfrSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
) : MsSqlServerJdbcResumablePartition(selectQueryGenerator, streamState, primaryKey) {

    // TODO: this needs to reflect lastRecord. Complete state needs to have last primary key value
    // in RFR case.
    override val completeState: OpaqueStateValue
        get() =
            MsSqlServerJdbcStreamStateValue.snapshotCheckpoint(
                primaryKey = checkpointColumns,
                primaryKeyCheckpoint =
                    checkpointColumns.map { upperBound?.get(0) ?: Jsons.nullNode() },
            )

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerJdbcStreamStateValue.snapshotCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
        )
}

/** RFR for CDC. */
class MsSqlServerJdbcCdcRfrSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
) : MsSqlServerJdbcResumablePartition(selectQueryGenerator, streamState, primaryKey) {
    init {
        log.info { "SGX lowerBound=$lowerBound, upperBound=$upperBound" }
    }

    override val completeState: OpaqueStateValue
        get() =
            MsSqlServerCdcInitialSnapshotStateValue.snapshotCheckpoint(
                primaryKey = checkpointColumns,
                primaryKeyCheckpoint =
                    checkpointColumns.map { upperBound?.get(0) ?: Jsons.nullNode() },
            )

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
    override val streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?
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

/**
 * Default implementation of a [JdbcPartition] for a splittable partition involving cursor columns.
 */
sealed class MsSqlServerJdbcCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    checkpointColumns: List<Field>,
    val cursor: Field,
    private val explicitCursorUpperBound: JsonNode?,
) :
    MsSqlServerJdbcResumablePartition(selectQueryGenerator, streamState, checkpointColumns),
    JdbcCursorPartition<DefaultJdbcStreamState> {

    val cursorUpperBound: JsonNode
        get() = explicitCursorUpperBound ?: streamState.cursorUpperBound!!

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec = SelectQuerySpec(SelectColumnMaxValue(cursor), from)
}

/**
 * Default implementation of a [JdbcPartition] for a splittable snapshot partition preceding a
 * cursor-based incremental sync.
 */
class MsSqlServerJdbcSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
    cursor: Field,
    cursorUpperBound: JsonNode?,
) :
    MsSqlServerJdbcCursorPartition(
        selectQueryGenerator,
        streamState,
        primaryKey,
        cursor,
        cursorUpperBound
    ) {
    // UpperBound is not used because the partition is not splittable.
    override val upperBound: List<JsonNode>? = null

    override val completeState: OpaqueStateValue
        get() =
            MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                cursorUpperBound,
                stream,
            )

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerJdbcStreamStateValue.snapshotWithCursorCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
            cursor,
            stream,
        )
}

/**
 * Default implementation of a [JdbcPartition] for a cursor incremental partition. These are always
 * splittable.
 */
class MsSqlServerJdbcCursorIncrementalPartition(
    selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
    cursor: Field,
    val cursorLowerBound: JsonNode,
    override val isLowerBoundIncluded: Boolean,
    cursorUpperBound: JsonNode?,
) :
    MsSqlServerJdbcCursorPartition(
        selectQueryGenerator,
        streamState,
        listOf(cursor),
        cursor,
        cursorUpperBound
    ) {

    init {
        log.info { "SGX cursorLowerBound=$cursorLowerBound, cursorUpperBound=$cursorUpperBound" }
    }

    override val lowerBound: List<JsonNode> = listOf(cursorLowerBound)
    override val upperBound: List<JsonNode>
        get() = listOf(cursorUpperBound)

    override val completeState: OpaqueStateValue
        get() =
            MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                cursorCheckpoint = cursorUpperBound,
                stream,
            )

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(
            cursor,
            cursorCheckpoint = lastRecord[cursor.id] ?: Jsons.nullNode(),
            stream,
        )
}
