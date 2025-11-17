/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.DataField
import io.airbyte.cdk.discover.NonEmittedField
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.read.And
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
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.WhereClauseLeafNode
import io.airbyte.cdk.read.WhereClauseNode
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons

val ctidField = NonEmittedField("ctid", StringFieldType)

sealed class PostgresSourceJdbcPartition(
    val selectQueryGenerator: SelectQueryGenerator,
    final override val streamState: PostgresSourceJdbcStreamState,
) : JdbcPartition<PostgresSourceJdbcStreamState> {
    val stream = streamState.stream
    val from = From(stream.name, stream.namespace)
}

sealed class PostgresSourceJdbcUnsplittablePartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
) : PostgresSourceJdbcPartition(selectQueryGenerator, streamState) {
    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    open val nonResumableQuerySpec = SelectQuerySpec(SelectColumns(stream.fields), from)

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns(stream.fields),
                From(stream.name, stream.namespace),
                limit = Limit(sampleSize.toLong())
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }
}

class PostgresSourceJdbcUnsplittableSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
) : PostgresSourceJdbcUnsplittablePartition(selectQueryGenerator, streamState) {
    override val completeState: OpaqueStateValue
        get() = PostgresSourceJdbcStreamStateValue.snapshotCompleted
}

class PostgresSourceJdbcUnsplittableSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
    val cursor: DataField,
) :
    PostgresSourceJdbcUnsplittablePartition(selectQueryGenerator, streamState),
    JdbcCursorPartition<PostgresSourceJdbcStreamState> {
    override val completeState: OpaqueStateValue
        get() =
            PostgresSourceJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                streamState.cursorUpperBound ?: Jsons.nullNode(),
            )

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec = SelectQuerySpec(SelectColumnMaxValue(cursor), from)
}

class PostgresSourceJdbcUnsplittableCursorIncrementalPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
    val cursor: DataField,
    val cursorLowerBound: JsonNode?,
    val isLowerBoundIncluded: Boolean,
    val explicitCursorUpperBound: JsonNode?,
) :
    PostgresSourceJdbcUnsplittablePartition(selectQueryGenerator, streamState),
    JdbcCursorPartition<PostgresSourceJdbcStreamState> {
    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns(stream.fields),
                From(stream.name, stream.namespace),
                limit = Limit(sampleSize.toLong())
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    val cursorUpperBound: JsonNode
        get() = explicitCursorUpperBound ?: streamState.cursorUpperBound ?: Jsons.nullNode()

    override val completeState: OpaqueStateValue
        get() =
            PostgresSourceJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                cursorUpperBound,
            )

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec = SelectQuerySpec(SelectColumnMaxValue(cursor), from)

    override val nonResumableQuerySpec: SelectQuerySpec
        get() = SelectQuerySpec(SelectColumns(stream.fields), from, where, OrderBy(cursor))

    val where: Where
        get() {
            val checkpointColumns: List<DataField> = listOf(cursor)
            val lowerBound: JsonNode? = cursorLowerBound
            val upperBound: JsonNode = cursorUpperBound
            val zippedLowerBound: List<Pair<DataField, JsonNode>> =
                lowerBound?.let { checkpointColumns.zip(listOf(it)) } ?: listOf()
            val lowerBoundDisj: List<WhereClauseNode> =
                zippedLowerBound.mapIndexed { idx: Int, (gtCol: DataField, gtValue: JsonNode) ->
                    val lastLeaf: WhereClauseLeafNode =
                        if (isLowerBoundIncluded && idx == checkpointColumns.size - 1) {
                            GreaterOrEqual(gtCol, gtValue)
                        } else {
                            Greater(gtCol, gtValue)
                        }
                    And(
                        zippedLowerBound.take(idx).map { (eqCol: DataField, eqValue: JsonNode) ->
                            Equal(eqCol, eqValue)
                        } + listOf(lastLeaf),
                    )
                }
            val zippedUpperBound: List<Pair<DataField, JsonNode>> =
                upperBound.let { checkpointColumns.zip(listOf(it)) }
            val upperBoundDisj: List<WhereClauseNode> =
                zippedUpperBound.mapIndexed { idx: Int, (leqCol: DataField, leqValue: JsonNode) ->
                    val lastLeaf: WhereClauseLeafNode =
                        if (idx < zippedUpperBound.size - 1) {
                            Lesser(leqCol, leqValue)
                        } else {
                            LesserOrEqual(leqCol, leqValue)
                        }
                    And(
                        zippedUpperBound.take(idx).map { (eqCol: DataField, eqValue: JsonNode) ->
                            Equal(eqCol, eqValue)
                        } + listOf(lastLeaf),
                    )
                }
            return Where(And(Or(lowerBoundDisj), Or(upperBoundDisj)))
        }
}

sealed class PostgresSourceSplittablePartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
    val checkpointColumns: List<DataField>,
) :
    PostgresSourceJdbcPartition(selectQueryGenerator, streamState),
    JdbcSplittablePartition<PostgresSourceJdbcStreamState> {
    abstract val lowerBound: JsonNode?
    abstract val upperBound: JsonNode?

    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    open val nonResumableQuerySpec: SelectQuerySpec
        get() = SelectQuerySpec(SelectColumns(listOf(ctidField) + stream.fields), from, where)

    override fun resumableQuery(limit: Long): SelectQuery {
        val querySpec =
            SelectQuerySpec(
                SelectColumns((listOf(ctidField) + stream.fields).distinct()),
                from,
                where,
                OrderBy(ctidField),
                Limit(limit)
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns((listOf(ctidField) + stream.fields).distinct()),
                From(stream.name, stream.namespace),
/*                where,*/
                /*OrderBy(listOf(ctidField)),*/
                limit = Limit(sampleSize.toLong())
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    val where: Where
        get() {
            val zippedLowerBound: List<Pair<DataField, JsonNode>> =
                lowerBound?.let { checkpointColumns.zip(listOf(it)) } ?: listOf()
            val lowerBoundDisj: List<WhereClauseNode> =
                zippedLowerBound.mapIndexed { idx: Int, (gtCol: DataField, gtValue: JsonNode) ->
                    val lastLeaf: WhereClauseLeafNode =
                        if (isLowerBoundIncluded && idx == checkpointColumns.size - 1) {
                            GreaterOrEqual(gtCol, gtValue)
                        } else {
                            Greater(gtCol, gtValue)
                        }
                    And(
                        zippedLowerBound.take(idx).map { (eqCol: DataField, eqValue: JsonNode) ->
                            Equal(eqCol, eqValue)
                        } + listOf(lastLeaf),
                    )
                }
            val zippedUpperBound: List<Pair<DataField, JsonNode>> =
                upperBound?.let { checkpointColumns.zip(listOf(it)) } ?: listOf()
            val upperBoundDisj: List<WhereClauseNode> =
                zippedUpperBound.mapIndexed { idx: Int, (leqCol: DataField, leqValue: JsonNode) ->
                    val lastLeaf: WhereClauseLeafNode =
                        if (idx < zippedUpperBound.size - 1) {
                            Lesser(leqCol, leqValue)
                        } else {
                            LesserOrEqual(leqCol, leqValue)
                        }
                    And(
                        zippedUpperBound.take(idx).map { (eqCol: DataField, eqValue: JsonNode) ->
                            Equal(eqCol, eqValue)
                        } + listOf(lastLeaf),
                    )
                }
            return Where(And(Or(lowerBoundDisj), Or(upperBoundDisj)))
        }

    open val isLowerBoundIncluded: Boolean = false
}

class PostgresSourceJdbcSplittableSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
    override val lowerBound: JsonNode?,
    override val upperBound: JsonNode?,
    val filenode: Filenode?,
    override val isLowerBoundIncluded: Boolean
) : PostgresSourceSplittablePartition(selectQueryGenerator, streamState, listOf(ctidField)) {
    override val completeState: OpaqueStateValue
        get() =
            when (upperBound) {
                null -> PostgresSourceJdbcStreamStateValue.snapshotCompleted
                else -> PostgresSourceJdbcStreamStateValue.snapshotCheckpoint(upperBound, filenode)
            }

    override fun incompleteState(lastRecord: SelectQuerier.ResultRow): OpaqueStateValue {
        return PostgresSourceJdbcStreamStateValue.snapshotCheckpoint(
            lastRecord.nonEmittedData.toJson()["ctid"],
            filenode
        )
    }
}

sealed class PostgresSourceCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
    checkpointColumns: List<DataField>,
    val cursor: DataField,
    val explicitCursorUpperBound: JsonNode?,
    val filenode: Filenode?
) :
    PostgresSourceSplittablePartition(selectQueryGenerator, streamState, checkpointColumns),
    JdbcCursorPartition<PostgresSourceJdbcStreamState> {

    val cursorUpperBound: JsonNode
        get() = explicitCursorUpperBound ?: streamState.cursorUpperBound ?: Jsons.nullNode()

    override val cursorUpperBoundQuery: SelectQuery
        get() = selectQueryGenerator.generate(cursorUpperBoundQuerySpec.optimize())

    val cursorUpperBoundQuerySpec = SelectQuerySpec(SelectColumnMaxValue(cursor), from)
}

class PostgresSourceJdbcSplittableSnapshotWithCursorPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
    override val lowerBound: JsonNode?,
    override val upperBound: JsonNode?,
    cursor: DataField,
    cursorUpperBound: JsonNode?,
    filenode: Filenode?,
    override val isLowerBoundIncluded: Boolean
) :
    PostgresSourceCursorPartition(
        selectQueryGenerator,
        streamState,
        listOf(ctidField),
        cursor,
        cursorUpperBound,
        filenode
    ) {

    override val completeState: OpaqueStateValue
        get() =
            when (upperBound) {
                null ->
                    PostgresSourceJdbcStreamStateValue.cursorIncrementalCheckpoint(
                        cursor,
                        cursorUpperBound,
                    )
                else ->
                    PostgresSourceJdbcStreamStateValue.snapshotWithCursorCheckpoint(
                        upperBound,
                        cursor,
                        cursorUpperBound,
                        filenode,
                    )
            }

    override fun incompleteState(lastRecord: SelectQuerier.ResultRow): OpaqueStateValue =
        PostgresSourceJdbcStreamStateValue.snapshotWithCursorCheckpoint(
            lastRecord.nonEmittedData.toJson()["ctid"],
            cursor,
            cursorUpperBound,
            filenode,
        )
}

class PostgresSourceJdbcCursorIncrementalPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: PostgresSourceJdbcStreamState,
    cursor: DataField,
    val cursorLowerBound: JsonNode,
    override val isLowerBoundIncluded: Boolean,
    cursorUpperBound: JsonNode?,
) :
    PostgresSourceCursorPartition(
        selectQueryGenerator,
        streamState,
        listOf(cursor),
        cursor,
        cursorUpperBound,
        null // Incremental partitions do not track filenode
    ) {
    override val lowerBound: JsonNode = cursorLowerBound
    override val upperBound: JsonNode
        get() = cursorUpperBound

    override val nonResumableQuerySpec: SelectQuerySpec
        get() = SelectQuerySpec(SelectColumns(stream.fields), from, where)

    override fun resumableQuery(limit: Long): SelectQuery {
        val querySpec =
            SelectQuerySpec(
                SelectColumns((stream.fields).distinct()),
                from,
                where,
                OrderBy(cursor),
                Limit(limit)
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns((stream.fields).distinct()),
                From(stream.name, stream.namespace),
                //                where,
                //orderBy = OrderBy(cursor),
                limit = Limit(sampleSize.toLong())
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    override val completeState: OpaqueStateValue
        get() =
            PostgresSourceJdbcStreamStateValue.cursorIncrementalCheckpoint(
                cursor,
                cursorUpperBound,
            )
    override fun incompleteState(lastRecord: SelectQuerier.ResultRow): OpaqueStateValue =
        PostgresSourceJdbcStreamStateValue.cursorIncrementalCheckpoint(
            cursor,
            lastRecord.data.toJson()[cursor.id] ?: Jsons.nullNode(),
        )
}
