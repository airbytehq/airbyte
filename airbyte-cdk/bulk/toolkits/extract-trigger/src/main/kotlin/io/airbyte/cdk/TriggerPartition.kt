/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
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
import kotlin.collections.distinct
import kotlin.collections.map
import kotlin.collections.mapIndexed
import kotlin.collections.plus
import kotlin.collections.take
import kotlin.collections.zip
import kotlin.let

sealed class TriggerPartition(
    val selectQueryGenerator: SelectQueryGenerator,
    final override val streamState: TriggerStreamState,
    protected val config: TriggerTableConfig,
) : JdbcPartition<TriggerStreamState> {
    val stream: Stream = streamState.stream
    val from = From(stream.name, stream.namespace)
}

/** Base class for trigger-based implementations of [JdbcPartition] for unsplittable partitions. */
sealed class TriggerUnsplittablePartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: TriggerStreamState,
    config: TriggerTableConfig,
) : TriggerPartition(selectQueryGenerator, streamState, config) {

    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    val nonResumableQuerySpec = SelectQuerySpec(SelectColumns(stream.fields), from)

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns(stream.fields),
                FromSample(stream.name, stream.namespace, sampleRateInvPow2, sampleSize),
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }
}

/** Trigger-based implementation of a [JdbcPartition] for an unsplittable snapshot partition. */
class TriggerUnsplittableSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: TriggerStreamState,
    config: TriggerTableConfig,
) : TriggerUnsplittablePartition(selectQueryGenerator, streamState, config) {

    override val completeState: OpaqueStateValue = DefaultJdbcStreamStateValue.snapshotCompleted
}

/**
 * Trigger-based implementation of a [JdbcPartition] for an unsplittable snapshot partition
 * preceding a cursor-based incremental sync.
 */
class TriggerUnsplittableSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: TriggerStreamState,
    val cursor: Field,
    config: TriggerTableConfig,
) :
    TriggerUnsplittablePartition(selectQueryGenerator, streamState, config),
    JdbcCursorPartition<TriggerStreamState> {

    override val completeState: OpaqueStateValue
        get() =
            DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                cursorCheckpoint = streamState.cursorUpperBound ?: Jsons.nullNode(),
            )

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec = SelectQuerySpec(SelectColumnMaxValue(cursor), from)
}

/** Base class for trigger-based implementations of [JdbcPartition] for splittable partitions. */
sealed class TriggerSplittablePartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: TriggerStreamState,
    config: TriggerTableConfig,
    val checkpointColumns: List<Field>,
    val triggerCdcPartitionState: TriggerCdcPartitionState? = null,
) :
    TriggerPartition(selectQueryGenerator, streamState, config),
    JdbcSplittablePartition<TriggerStreamState> {

    init {
        streamState.isReadingFromTriggerTable =
            triggerCdcPartitionState == TriggerCdcPartitionState.INCREMENTAL
    }

    abstract val lowerBound: List<JsonNode>?
    abstract val upperBound: List<JsonNode>?

    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    val queryTableColumns =
        if (triggerCdcPartitionState == TriggerCdcPartitionState.INCREMENTAL)
            config.getTriggerTableSchemaFromStream(stream)
        else stream.fields
    val triggerTableName =
        TriggerTableConfig.TRIGGER_TABLE_PREFIX + stream.namespace + '_' + stream.name
    val queryTableFrom =
        if (triggerCdcPartitionState == TriggerCdcPartitionState.INCREMENTAL)
            From(
                triggerTableName,
                TriggerTableConfig.TRIGGER_TABLE_NAMESPACE,
            )
        else from
    val nonResumableQuerySpec: SelectQuerySpec
        get() = SelectQuerySpec(SelectColumns(queryTableColumns), queryTableFrom, where)

    override fun resumableQuery(limit: Long): SelectQuery {
        val querySpec =
            SelectQuerySpec(
                SelectColumns((queryTableColumns + checkpointColumns).distinct()),
                queryTableFrom,
                where,
                OrderBy(checkpointColumns),
                Limit(limit),
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val samplingTableName =
            if (triggerCdcPartitionState == TriggerCdcPartitionState.INCREMENTAL) triggerTableName
            else stream.name
        val samplingNamespace =
            if (triggerCdcPartitionState == TriggerCdcPartitionState.INCREMENTAL)
                TriggerTableConfig.TRIGGER_TABLE_NAMESPACE
            else stream.namespace
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns((queryTableColumns + checkpointColumns).distinct()),
                FromSample(samplingTableName, samplingNamespace, sampleRateInvPow2, sampleSize),
                where,
                OrderBy(checkpointColumns),
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

/** Default implementation of a [JdbcPartition] for a splittable snapshot partition. */
class TriggerSplittableSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: TriggerStreamState,
    config: TriggerTableConfig,
    primaryKey: List<Field>,
    triggerCdcPartitionState: TriggerCdcPartitionState? = null,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
) :
    TriggerSplittablePartition(
        selectQueryGenerator,
        streamState,
        config,
        primaryKey,
        triggerCdcPartitionState,
    ) {

    override val completeState: OpaqueStateValue
        get() =
            when (upperBound) {
                null -> DefaultJdbcStreamStateValue.snapshotCompleted
                else ->
                    DefaultJdbcStreamStateValue.snapshotCheckpoint(
                        primaryKey = checkpointColumns,
                        primaryKeyCheckpoint = upperBound,
                    )
            }

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        DefaultJdbcStreamStateValue.snapshotCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
        )
}

/**
 * Default implementation of a [JdbcPartition] for a splittable partition involving cursor columns.
 */
sealed class TriggerCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: TriggerStreamState,
    config: TriggerTableConfig,
    checkpointColumns: List<Field>,
    triggerCdcPartitionState: TriggerCdcPartitionState? = null,
    val cursor: Field,
    private val explicitCursorUpperBound: JsonNode?,
) :
    TriggerSplittablePartition(
        selectQueryGenerator,
        streamState,
        config,
        checkpointColumns,
        triggerCdcPartitionState,
    ),
    JdbcCursorPartition<TriggerStreamState> {

    val cursorUpperBound: JsonNode
        get() = explicitCursorUpperBound ?: streamState.cursorUpperBound ?: Jsons.nullNode()
    val cursorUpperBoundFrom: From =
        if (triggerCdcPartitionState == null) from
        else
            From(
                triggerTableName,
                TriggerTableConfig.TRIGGER_TABLE_NAMESPACE,
            )

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec =
        SelectQuerySpec(SelectColumnMaxValue(cursor), cursorUpperBoundFrom)
}

/**
 * Trigger-based implementation of a [JdbcPartition] for a splittable snapshot partition preceding a
 * cursor-based incremental sync.
 */
class TriggerSplittableSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: TriggerStreamState,
    config: TriggerTableConfig,
    primaryKey: List<Field>,
    triggerCdcPartitionState: TriggerCdcPartitionState? = null,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
    cursor: Field,
    cursorUpperBound: JsonNode?,
) :
    TriggerCursorPartition(
        selectQueryGenerator,
        streamState,
        config,
        primaryKey,
        triggerCdcPartitionState,
        cursor,
        cursorUpperBound,
    ) {

    override val completeState: OpaqueStateValue
        get() =
            when (upperBound) {
                null ->
                    DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(
                        cursor,
                        cursorUpperBound,
                    )
                else ->
                    DefaultJdbcStreamStateValue.snapshotWithCursorCheckpoint(
                        primaryKey = checkpointColumns,
                        primaryKeyCheckpoint = upperBound,
                        cursor,
                        cursorUpperBound,
                    )
            }

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        DefaultJdbcStreamStateValue.snapshotWithCursorCheckpoint(
            primaryKey = checkpointColumns,
            primaryKeyCheckpoint = checkpointColumns.map { lastRecord[it.id] ?: Jsons.nullNode() },
            cursor,
            cursorUpperBound,
        )
}

/**
 * Trigger-based implementation of a [JdbcPartition] for a cursor incremental partition. These are
 * always splittable.
 */
class TriggerCursorIncrementalPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: TriggerStreamState,
    config: TriggerTableConfig,
    cursor: Field,
    triggerCdcPartitionState: TriggerCdcPartitionState? = null,
    val cursorLowerBound: JsonNode,
    override val isLowerBoundIncluded: Boolean,
    cursorUpperBound: JsonNode?,
) :
    TriggerCursorPartition(
        selectQueryGenerator,
        streamState,
        config,
        listOf(cursor),
        triggerCdcPartitionState,
        cursor,
        cursorUpperBound,
    ) {

    override val lowerBound: List<JsonNode> = listOf(cursorLowerBound)
    override val upperBound: List<JsonNode>
        get() = listOf(cursorUpperBound)

    override val completeState: OpaqueStateValue
        get() =
            DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                cursorCheckpoint = cursorUpperBound,
            )

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue =
        DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(
            cursor,
            cursorCheckpoint = lastRecord[cursor.id] ?: Jsons.nullNode(),
        )
}

// SNAPSHOT indicates the stream hasn't had a snapshot completed yet and the partition need to read
// data from the source table.
// INCREMENTAL indicates the stream has had a snapshot completed and the partition need to read
// change from trigger table.
enum class TriggerCdcPartitionState {
    SNAPSHOT,
    INCREMENTAL,
}
