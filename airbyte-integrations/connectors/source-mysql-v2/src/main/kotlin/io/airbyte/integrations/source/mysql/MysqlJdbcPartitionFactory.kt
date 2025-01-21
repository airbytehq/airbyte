/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.LeafAirbyteSchemaType
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
    val selectQueryGenerator: MysqlSourceOperations,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        MysqlJdbcPartition,
    > {

    private val streamStates = ConcurrentHashMap<String, DefaultJdbcStreamState>()

    override fun streamState(stream: Stream): DefaultJdbcStreamState =
        streamStates.getOrPut(stream.label) { DefaultJdbcStreamState(sharedState, stream) }

    private fun coldStart(streamState: DefaultJdbcStreamState): MysqlJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (
            stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH ||
                sharedState.configuration.global
        ) {
            if (pkChosenFromCatalog.isEmpty()) {
                return MysqlJdbcNonResumableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }
            return MysqlJdbcSnapshotPartition(
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
            return MysqlJdbcNonResumableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog
            )
        }
        return MysqlJdbcSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            pkChosenFromCatalog,
            lowerBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )
    }

    /**
     * Flowchart:
     * 1. If the input state is null - using coldstart.
     * ```
     *    a. If it's global but without PK, use non-resumable  snapshot.
     *    b. If it's global with PK, use snapshot.
     *    c. If it's not global, use snapshot with cursor.
     * ```
     * 2. If the input state is not null -
     * ```
     *    a. If it's in global mode, JdbcPartitionFactory will not handle this. (TODO)
     *    b. If it's cursor based, it could be either in PK read phase (initial read) or
     *       cursor read phase (incremental read). This is differentiated by the stateType.
     *      i. In PK read phase, use snapshot with cursor. If no PKs were found,
     *         use non-resumable snapshot with cursor.
     *      ii. In cursor read phase, use cursor incremental.
     * ```
     */
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
            // TODO: This should consider v1 state format for CDC initial read and return
            // a MysqlJdbcSnapshotPartition, or a different partition if we can't reuse
            // MysqlJdbcStreamStateValue.
            return null
        } else {
            if (sv.stateType != "cursor_based") {
                // Loading value from catalog. Note there could be unexpected behaviors if user
                // updates their schema but did not reset their state.
                val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
                val pkLowerBound: JsonNode = Jsons.valueToTree(sv.pkValue)
                val cursorChosenFromCatalog: Field =
                    stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

                // in a state where it's still in primary_key read part.
                return MysqlJdbcSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = listOf(pkLowerBound),
                    cursorChosenFromCatalog,
                    cursorUpperBound = null,
                )
            }
            // resume back to cursor based increment.
            val cursor: Field = stream.fields.find { it.id == sv.cursorField.first() } as Field
            val cursorCheckpoint: JsonNode =
                when (cursor.type.airbyteSchemaType) {
                    is LeafAirbyteSchemaType ->
                        when (cursor.type.airbyteSchemaType as LeafAirbyteSchemaType) {
                            LeafAirbyteSchemaType.INTEGER -> {
                                Jsons.valueToTree(sv.cursors.toInt())
                            }
                            LeafAirbyteSchemaType.NUMBER -> {
                                Jsons.valueToTree(sv.cursors.toDouble())
                            }
                            else -> Jsons.valueToTree(sv.cursors)
                        }
                    else ->
                        throw IllegalStateException(
                            "Cursor field must be leaf type but is ${cursor.type.airbyteSchemaType}."
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
