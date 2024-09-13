/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.InvalidCursor
import io.airbyte.cdk.output.InvalidPrimaryKey
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.SyncMode
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/** Default implementation of [JdbcPartitionFactory]. */
@Singleton
class DefaultJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val handler: CatalogValidationFailureHandler,
    val selectQueryGenerator: SelectQueryGenerator,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        DefaultJdbcPartition,
    > {

    private val streamStates = ConcurrentHashMap<String, DefaultJdbcStreamState>()

    override fun streamState(stream: Stream): DefaultJdbcStreamState =
        streamStates.getOrPut(stream.label) { DefaultJdbcStreamState(sharedState, stream) }

    override fun create(
        stream: Stream,
        opaqueStateValue: OpaqueStateValue?,
    ): DefaultJdbcPartition? {
        val streamState: DefaultJdbcStreamState = streamState(stream)
        if (opaqueStateValue == null) {
            return coldStart(streamState)
        }
        val sv: DefaultJdbcStreamStateValue =
            Jsons.treeToValue(opaqueStateValue, DefaultJdbcStreamStateValue::class.java)
        val pkMap: Map<Field, JsonNode> =
            sv.pkMap(stream)
                ?: run {
                    handler.accept(ResetStream(stream.name, stream.namespace))
                    streamState.reset()
                    return coldStart(streamState)
                }
        val cursorPair: Pair<Field, JsonNode>? =
            if (sv.cursors.isEmpty()) {
                null
            } else {
                sv.cursorPair(stream)
                    ?: run {
                        handler.accept(ResetStream(stream.name, stream.namespace))
                        streamState.reset()
                        return coldStart(streamState)
                    }
            }

        val isCursorBasedIncremental: Boolean =
            stream.configuredSyncMode == SyncMode.INCREMENTAL && !configuration.global

        return if (cursorPair == null) {
            if (isCursorBasedIncremental) {
                handler.accept(ResetStream(stream.name, stream.namespace))
                streamState.reset()
                coldStart(streamState)
            } else if (pkMap.isEmpty()) {
                // Snapshot complete.
                null
            } else {
                // Snapshot ongoing.
                DefaultJdbcSplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    primaryKey = pkMap.keys.toList(),
                    lowerBound = pkMap.values.toList(),
                    upperBound = null
                )
            }
        } else {
            val (cursor: Field, cursorCheckpoint: JsonNode) = cursorPair
            if (!isCursorBasedIncremental) {
                handler.accept(ResetStream(stream.name, stream.namespace))
                streamState.reset()
                coldStart(streamState)
            } else if (pkMap.isNotEmpty()) {
                // Snapshot ongoing.
                DefaultJdbcSplittableSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    primaryKey = pkMap.keys.toList(),
                    lowerBound = pkMap.values.toList(),
                    upperBound = null,
                    cursor,
                    cursorUpperBound = cursorCheckpoint,
                )
            } else if (cursorCheckpoint == streamState.cursorUpperBound) {
                // Incremental complete.
                null
            } else {
                // Incremental ongoing.
                DefaultJdbcCursorIncrementalPartition(
                    selectQueryGenerator,
                    streamState,
                    cursor,
                    cursorLowerBound = cursorCheckpoint,
                    isLowerBoundIncluded = true,
                    cursorUpperBound = streamState.cursorUpperBound,
                )
            }
        }
    }

    private fun DefaultJdbcStreamStateValue.pkMap(stream: Stream): Map<Field, JsonNode>? {
        if (primaryKey.isEmpty()) {
            return mapOf()
        }
        val fields: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (primaryKey.keys != fields.map { it.id }.toSet()) {
            handler.accept(
                InvalidPrimaryKey(stream.name, stream.namespace, primaryKey.keys.toList()),
            )
            return null
        }
        return fields.associateWith { primaryKey[it.id]!! }
    }

    private fun DefaultJdbcStreamStateValue.cursorPair(stream: Stream): Pair<Field, JsonNode>? {
        if (cursors.size > 1) {
            handler.accept(
                InvalidCursor(stream.name, stream.namespace, cursors.keys.toString()),
            )
            return null
        }
        val cursorLabel: String = cursors.keys.first()
        val cursor: FieldOrMetaField? = stream.fields.find { it.id == cursorLabel }
        if (cursor !is Field) {
            handler.accept(
                InvalidCursor(stream.name, stream.namespace, cursorLabel),
            )
            return null
        }
        if (stream.configuredCursor != cursor) {
            handler.accept(
                InvalidCursor(stream.name, stream.namespace, cursorLabel),
            )
            return null
        }
        return cursor to cursors[cursorLabel]!!
    }

    private fun coldStart(streamState: DefaultJdbcStreamState): DefaultJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (stream.configuredSyncMode == SyncMode.FULL_REFRESH || configuration.global) {
            if (pkChosenFromCatalog.isEmpty()) {
                return DefaultJdbcUnsplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }
            return DefaultJdbcSplittableSnapshotPartition(
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
            return DefaultJdbcUnsplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog
            )
        }
        return DefaultJdbcSplittableSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            pkChosenFromCatalog,
            lowerBound = null,
            upperBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )
    }

    val configuration: JdbcSourceConfiguration = sharedState.configuration

    override fun split(
        unsplitPartition: DefaultJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<DefaultJdbcPartition> {
        val splitPartitionBoundaries: List<DefaultJdbcStreamStateValue> by lazy {
            opaqueStateValues.map { Jsons.treeToValue(it, DefaultJdbcStreamStateValue::class.java) }
        }
        return when (unsplitPartition) {
            is DefaultJdbcSplittableSnapshotPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is DefaultJdbcSplittableSnapshotWithCursorPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is DefaultJdbcCursorIncrementalPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is DefaultJdbcUnsplittableSnapshotPartition -> listOf(unsplitPartition)
            is DefaultJdbcUnsplittableSnapshotWithCursorPartition -> listOf(unsplitPartition)
        }
    }

    private fun DefaultJdbcSplittableSnapshotPartition.split(
        splitPointValues: List<DefaultJdbcStreamStateValue>
    ): List<DefaultJdbcSplittableSnapshotPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            DefaultJdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                primaryKey = checkpointColumns,
                lowerBound,
                upperBound,
            )
        }
    }

    private fun DefaultJdbcSplittableSnapshotWithCursorPartition.split(
        splitPointValues: List<DefaultJdbcStreamStateValue>
    ): List<DefaultJdbcSplittableSnapshotWithCursorPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            DefaultJdbcSplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                primaryKey = checkpointColumns,
                lowerBound,
                upperBound,
                cursor,
                cursorUpperBound,
            )
        }
    }

    private fun DefaultJdbcCursorIncrementalPartition.split(
        splitPointValues: List<DefaultJdbcStreamStateValue>
    ): List<DefaultJdbcCursorIncrementalPartition> {
        val inners: List<JsonNode> = splitPointValues.mapNotNull { it.cursorPair(stream)?.second }
        val lbs: List<JsonNode> = listOf(cursorLowerBound) + inners
        val ubs: List<JsonNode> = inners + listOf(cursorUpperBound)
        return lbs.zip(ubs).mapIndexed { idx: Int, (lowerBound, upperBound) ->
            DefaultJdbcCursorIncrementalPartition(
                selectQueryGenerator,
                streamState,
                cursor,
                lowerBound,
                isLowerBoundIncluded = idx == 0,
                upperBound,
            )
        }
    }
}
