package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcCursorIncrementalPartition
import io.airbyte.cdk.read.DefaultJdbcPartition
import io.airbyte.cdk.read.DefaultJdbcPartitionFactory
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcSplittableSnapshotPartition
import io.airbyte.cdk.read.DefaultJdbcSplittableSnapshotWithCursorPartition
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.DefaultJdbcUnsplittableSnapshotPartition
import io.airbyte.cdk.read.DefaultJdbcUnsplittableSnapshotWithCursorPartition
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons

class MysqlJdbcPartitionFactory(val base: DefaultJdbcPartitionFactory) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        DefaultJdbcPartition,
        >  by base {

    override fun create(
        stream: Stream,
        opaqueStateValue: OpaqueStateValue?,
    ): DefaultJdbcPartition? {
        val streamState: DefaultJdbcStreamState = streamState(stream)
        if (opaqueStateValue == null) {
            return base.coldStart(streamState)
        }
        val sv: MysqlJdbcStreamStateValue =
            Jsons.treeToValue(opaqueStateValue, MysqlJdbcStreamStateValue::class.java)

        // todo: implement PK (CDC initial state)
        val isCursorBasedIncremental: Boolean =
            stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL && !base.configuration.global

        if (!isCursorBasedIncremental) {
            // todo: Implement me for cdc initial read states.
            throw IllegalStateException("To be implemented.")
        } else {
            if (sv.stateType != "cursor_based") {
                throw IllegalStateException("Expecting state to have cursor_based state type.")
            }
            // resume back to cursor based increment.
            val cursor: Field = stream.fields.find { it.id == sv.cursors } as Field
            // Compose a jsonnode of cursor label to cursor value to fit in DefaultJdbcCursorIncrementalPartition
            val cursorCheckpoint: JsonNode = Jsons.valueToTree(mapOf(sv.cursorField.first() to sv.cursors))
            DefaultJdbcCursorIncrementalPartition(
                base.selectQueryGenerator,
                streamState,
                cursor,
                cursorLowerBound = cursorCheckpoint,
                isLowerBoundIncluded = true,
                cursorUpperBound = streamState.cursorUpperBound,
            )
        }

    }

    override fun split(
        unsplitPartition: DefaultJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<DefaultJdbcPartition> {
        val splitPartitionBoundaries: List<MysqlJdbcStreamStateValue> by lazy {
            opaqueStateValues.map { Jsons.treeToValue(it, MysqlJdbcStreamStateValue::class.java) }
        }
        return when (unsplitPartition) {
            is DefaultJdbcSplittableSnapshotWithCursorPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is DefaultJdbcCursorIncrementalPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is DefaultJdbcUnsplittableSnapshotWithCursorPartition -> listOf(unsplitPartition)
            else -> throw IllegalStateException("Unsupported partition type: $unsplitPartition")
        }
    }



}



