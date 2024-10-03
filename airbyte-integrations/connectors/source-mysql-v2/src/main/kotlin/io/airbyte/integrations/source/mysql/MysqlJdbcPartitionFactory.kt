/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.LeafAirbyteType
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Primary
import java.util.concurrent.ConcurrentHashMap
import javax.inject.Singleton

@Primary
@Singleton
class MysqlJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: MysqlSourceOperations
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        MysqlJdbcPartition,
    > {

    private val streamStates = ConcurrentHashMap<String, DefaultJdbcStreamState>()

    override fun streamState(stream: Stream): DefaultJdbcStreamState =
        streamStates.getOrPut(stream.label) { DefaultJdbcStreamState(sharedState, stream) }

    fun coldStart(streamState: DefaultJdbcStreamState): MysqlJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (
            stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH ||
                sharedState.configuration.global
        ) {
            if (pkChosenFromCatalog.isEmpty()) {
                return MysqlJdbcUnsplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }
            return MysqlJdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                pkChosenFromCatalog,
                lowerBound = null,
                upperBound = null,
            )
        }

        val cursorChosenFromCatalog: Field =
            stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

        if (pkChosenFromCatalog.isEmpty()) {
            return MysqlJdbcUnsplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog
            )
        }
        return MysqlJdbcSplittableSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            pkChosenFromCatalog,
            lowerBound = null,
            upperBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )
    }

    override fun create(
        stream: Stream,
        opaqueStateValue: OpaqueStateValue?,
    ): MysqlJdbcPartition? {
        val streamState: DefaultJdbcStreamState = streamState(stream)
        if (opaqueStateValue == null) {
            return coldStart(streamState)
        }
        val sv: MysqlJdbcStreamStateValue =
            Jsons.treeToValue(opaqueStateValue, MysqlJdbcStreamStateValue::class.java)

        val isCursorBasedIncremental: Boolean =
            stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL &&
                !sharedState.configuration.global

        if (!isCursorBasedIncremental) {
            // todo: Implement me for cdc initial read states.
            throw IllegalStateException("Should reset.")
        } else {
            if (sv.stateType != "cursor_based") {
                // Loading value from catalog. Note there could be unexpected behaviors if user
                // updates their schema but did not reset their state.
                val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
                val pkLowerBound: JsonNode = Jsons.valueToTree(sv.pkValue)
                val cursorChosenFromCatalog: Field =
                    stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

                // in a state where it's still in primary_key read part.
                return MysqlJdbcSplittableSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = listOf(pkLowerBound),
                    upperBound = null,
                    cursorChosenFromCatalog,
                    cursorUpperBound = null,
                )
            }
            // resume back to cursor based increment.
            val cursor: Field = stream.fields.find { it.id == sv.cursorField.first() } as Field
            var cursorCheckpoint: JsonNode =
                when (cursor.type.airbyteType) {
                    is LeafAirbyteType ->
                        when (cursor.type.airbyteType as LeafAirbyteType) {
                            LeafAirbyteType.INTEGER -> {
                                Jsons.valueToTree(sv.cursors.toInt())
                            }
                            LeafAirbyteType.NUMBER -> {
                                Jsons.valueToTree(sv.cursors.toDouble())
                            }
                            else -> Jsons.valueToTree(sv.cursors)
                        }
                    else ->
                        throw IllegalStateException(
                            "Cursor field must be leaf type but is ${cursor.type.airbyteType}."
                        )
                }
            // Compose a jsonnode of cursor label to cursor value to fit in
            // DefaultJdbcCursorIncrementalPartition
            if (cursorCheckpoint == streamState.cursorUpperBound) {
                // Incremental complete.
                return null
            }
            return MysqlJdbcCursorIncrementalPartition(
                selectQueryGenerator,
                streamState,
                cursor,
                cursorLowerBound = cursorCheckpoint,
                isLowerBoundIncluded = false,
                cursorUpperBound = streamState.cursorUpperBound,
            )
        }
    }

    override fun split(
        unsplitPartition: MysqlJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<MysqlJdbcPartition> {
        // At this moment we don't support split on within mysql stream in any mode.
        return listOf(unsplitPartition)
    }
}
