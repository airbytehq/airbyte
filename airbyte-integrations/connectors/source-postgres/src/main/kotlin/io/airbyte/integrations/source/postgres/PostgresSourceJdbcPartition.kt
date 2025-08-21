package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.DataField
import io.airbyte.cdk.discover.NonEmittedField
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.Equal
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.FromSample
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.GreaterOrEqual
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcSplittablePartition
import io.airbyte.cdk.read.Lesser
import io.airbyte.cdk.read.LesserOrEqual
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.Or
import io.airbyte.cdk.read.OrderBy
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
import io.airbyte.integrations.source.postgres.ctid.Ctid

sealed class PostgresSourceJdbcPartition(
    val selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
) : JdbcPartition<DefaultJdbcStreamState> {
    val ctidField = NonEmittedField("ctid", StringFieldType)
    val stream = streamState.stream
    val from = From(stream.name, stream.namespace)
}

class PostgresSourceJdbcNonResumableSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
) : PostgresSourceJdbcPartition(selectQueryGenerator, streamState) {
    override val completeState: OpaqueStateValue /*PostgresSorouceJdbcStreamStateValue.snapshotCompleted*/
        get() = Jsons.nullNode() // TEMP

    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    val nonResumableQuerySpec = SelectQuerySpec(SelectColumns(
        listOf(ctidField) + stream.fields
    ), from)

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize

        val querySpec =
            SelectQuerySpec(SelectColumns(listOf(ctidField) + stream.fields),
                FromSample(stream.name, stream.namespace, sampleRateInvPow2, sampleSize),
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }


}

sealed class PostgresSourceSplittablePartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    val checkpointColumns: List<DataField>,
) : PostgresSourceJdbcPartition(selectQueryGenerator, streamState),
    JdbcSplittablePartition<DefaultJdbcStreamState>{
    abstract val lowerBound: Ctid?
    abstract val upperBound: Ctid?

    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    val nonResumableQuerySpec: SelectQuerySpec
        get() = SelectQuerySpec(SelectColumns(listOf(ctidField) + stream.fields), from, where)

    override fun resumableQuery(limit: Long): SelectQuery {
        val querySpec =
            SelectQuerySpec(
                SelectColumns((listOf(ctidField) + stream.fields + checkpointColumns).distinct()),
                from,
                where,
                OrderBy(checkpointColumns),
                Limit(limit)
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(
                SelectColumns((listOf(ctidField) + stream.fields).distinct()),
                FromSample(stream.name, stream.namespace, sampleRateInvPow2, sampleSize),
                where,
                OrderBy(listOf(ctidField)), // TODO: check here
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }

    val where: Where
        get() {
            val zippedLowerBound: List<Pair<DataField, JsonNode>> =
                lowerBound?.let { listOf(ctidField to Jsons.textNode(lowerBound.toString())) } ?: listOf()
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
                upperBound?.let { listOf(ctidField to Jsons.textNode(upperBound.toString())) } ?: listOf()
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
    override val streamState: DefaultJdbcStreamState,
    primaryKey: List<DataField>,
    override val lowerBound: Ctid?,
    override val upperBound: Ctid?,
) : PostgresSourceSplittablePartition(selectQueryGenerator, streamState, primaryKey) {
    override val completeState: OpaqueStateValue
        get() =
        when (upperBound) {
            null -> PostgresSourceJdbcStreamStateValue.snapshotCompleted
            else -> PostgresSourceJdbcStreamStateValue.snapshotCheckpoint(
                 Jsons.textNode(upperBound.toString())
            )
        }

//

    override fun incompleteState(lastRecord: SelectQuerier.ResultRow): OpaqueStateValue {
        return PostgresSourceJdbcStreamStateValue.snapshotCheckpoint(
            lastRecord.nonEmittedData.toJson()["ctid"]
        )

    }
}
