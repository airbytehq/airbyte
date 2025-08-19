package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.FromSample
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons

sealed class PostgresSourceJdbcPartition(
    val selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
) : JdbcPartition<DefaultJdbcStreamState> {
    val stream = streamState.stream
    val from = From(stream.name, stream.namespace)

    override val nonResumableQuery: SelectQuery
        get() = selectQueryGenerator.generate(nonResumableQuerySpec.optimize())

    open val nonResumableQuerySpec = SelectQuerySpec(SelectColumns(stream.fields), from)

    override fun samplingQuery(sampleRateInvPow2: Int): SelectQuery {
        val sampleSize: Int = streamState.sharedState.maxSampleSize
        val querySpec =
            SelectQuerySpec(SelectColumns(stream.fields),
                FromSample(stream.name, stream.namespace, sampleRateInvPow2, sampleSize),
            )
        return selectQueryGenerator.generate(querySpec.optimize())
    }
}

class PostgresSourceJdbcNonResumableSnapshotPartition(
    selectQueryGenerator: SelectQueryGenerator,
    override val streamState: DefaultJdbcStreamState,
) : PostgresSourceJdbcPartition(selectQueryGenerator, streamState) {
    override val completeState: OpaqueStateValue = /*PostgresSorouceJdbcStreamStateValue.snapshotCompleted*/
        Jsons.nullNode() // TEMP

}
