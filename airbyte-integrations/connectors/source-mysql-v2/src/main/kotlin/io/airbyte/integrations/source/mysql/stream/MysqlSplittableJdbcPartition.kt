package io.airbyte.integrations.source.mysql.stream

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.DefaultJdbcSplittablePartition
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.util.Jsons

class  {
}

/** Default implementation of a [JdbcPartition] for a splittable snapshot partition. */
class MysqlSplittableJdbcPartition(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: DefaultJdbcStreamState,
    primaryKey: List<Field>,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
) : JdbcPartition<DefaultJdbcStreamState> (selectQueryGenerator, streamState, primaryKey) {

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
