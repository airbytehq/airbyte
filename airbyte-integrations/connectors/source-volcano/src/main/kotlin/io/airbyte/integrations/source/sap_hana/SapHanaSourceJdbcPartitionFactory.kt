/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.InvalidCursor
import io.airbyte.cdk.output.InvalidPrimaryKey
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Primary
@Singleton
class SapHanaSourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val handler: CatalogValidationFailureHandler,
    val selectQueryGenerator: SapHanaSourceOperations,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        SapHanaJdbcStreamState,
        SapHanaSourceJdbcPartition,
    > {

    private val streamStates = ConcurrentHashMap<StreamIdentifier, SapHanaJdbcStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): SapHanaJdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            SapHanaJdbcStreamState(sharedState, streamFeedBootstrap)
        }

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): SapHanaSourceJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: SapHanaJdbcStreamState = streamState(streamFeedBootstrap)
        val opaqueStateValue: OpaqueStateValue? = streamFeedBootstrap.currentState
        if (opaqueStateValue == null) {
            return coldStart(streamState)
        }
        val sv: SapHanaSourceJdbcStreamStateValue =
            Jsons.treeToValue(opaqueStateValue, SapHanaSourceJdbcStreamStateValue::class.java)
        val pkMap: Map<Field, JsonNode> =
            sv.pkMap(stream)
                ?: run {
                    handler.accept(ResetStream(stream.id))
                    streamState.reset()
                    return coldStart(streamState)
                }
        val cursorPair: Pair<Field, JsonNode>? =
            if (sv.cursors.isEmpty()) {
                null
            } else {
                sv.cursorPair(stream)
                    ?: run {
                        handler.accept(ResetStream(stream.id))
                        streamState.reset()
                        return coldStart(streamState)
                    }
            }

        // Incremental sync applies to CDC or user defined cursor based incremental.
        val isIncrementalSync: Boolean = stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL

        return if (cursorPair == null) {
            if (isIncrementalSync) {
                handler.accept(ResetStream(stream.id))
                streamState.reset()
                coldStart(streamState)
            } else if (pkMap.isEmpty()) {
                // Snapshot complete.
                null
            } else {
                // Snapshot ongoing.
                SapHanaJdbcSplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    primaryKey = pkMap.keys.toList(),
                    lowerBound = pkMap.values.toList(),
                    upperBound = null,
                )
            }
        } else {
            val (cursor: Field, cursorCheckpoint: JsonNode) = cursorPair
            val triggerCdcPartitionState =
                if (cursor.id == TriggerTableConfig.CURSOR_FIELD.id)
                    TriggerCdcPartitionState.INCREMENTAL
                else null

            if (!isIncrementalSync) {
                handler.accept(ResetStream(stream.id))
                streamState.reset()
                coldStart(streamState)
            } else if (pkMap.isNotEmpty()) {
                // Snapshot ongoing.
                SapHanaJdbcSplittableSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    primaryKey = pkMap.keys.toList(),
                    triggerCdcPartitionState,
                    lowerBound = pkMap.values.toList(),
                    upperBound = null,
                    cursor,
                    cursorUpperBound = cursorCheckpoint,
                )
            } else if (cursorCheckpoint == streamState.cursorUpperBound) {
                // Incremental sync complete.
                null
            } else {
                // Incremental sync ongoing.
                SapHanaJdbcCursorIncrementalPartition(
                    selectQueryGenerator,
                    streamState,
                    cursor,
                    triggerCdcPartitionState,
                    cursorLowerBound = cursorCheckpoint,
                    isLowerBoundIncluded = true,
                    cursorUpperBound = streamState.cursorUpperBound,
                )
            }
        }
    }

    private fun SapHanaSourceJdbcStreamStateValue.pkMap(stream: Stream): Map<Field, JsonNode>? {
        if (primaryKey.isEmpty()) {
            return mapOf()
        }
        val fields: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (primaryKey.keys != fields.map { it.id }.toSet()) {
            handler.accept(
                InvalidPrimaryKey(stream.id, primaryKey.keys.toList()),
            )
            return null
        }
        return fields.associateWith { primaryKey[it.id]!! }
    }

    private fun SapHanaSourceJdbcStreamStateValue.cursorPair(
        stream: Stream
    ): Pair<Field, JsonNode>? {
        if (cursors.size > 1) {
            handler.accept(
                InvalidCursor(stream.id, cursors.keys.toString()),
            )
            return null
        }
        val cursorLabel: String = cursors.keys.first()
        val cursor: FieldOrMetaField? =
            stream.schema.find { it.id == cursorLabel }
                ?: TriggerTableConfig.SCHEMA.find { it.id == cursorLabel }
        if (cursor !is Field) {
            handler.accept(
                InvalidCursor(stream.id, cursorLabel),
            )
            return null
        }
        if (stream.configuredCursor != cursor) {
            handler.accept(
                InvalidCursor(stream.id, cursorLabel),
            )
            return null
        }
        return cursor to cursors[cursorLabel]!!
    }

    private fun coldStart(streamState: SapHanaJdbcStreamState): SapHanaSourceJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            if (pkChosenFromCatalog.isEmpty()) {
                return SapHanaJdbcUnsplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }
            return SapHanaJdbcSplittableSnapshotPartition(
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
            return SapHanaJdbcUnsplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog,
            )
        }
        val triggerCdcPartitionState =
            if (configuration.isCdc()) TriggerCdcPartitionState.SNAPSHOT else null
        return SapHanaJdbcSplittableSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            pkChosenFromCatalog,
            triggerCdcPartitionState,
            lowerBound = null,
            upperBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )
    }

    val configuration: SapHanaSourceConfiguration =
        sharedState.configuration as SapHanaSourceConfiguration

    override fun split(
        unsplitPartition: SapHanaSourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<SapHanaSourceJdbcPartition> {
        val splitPartitionBoundaries: List<SapHanaSourceJdbcStreamStateValue> by lazy {
            opaqueStateValues.map {
                Jsons.treeToValue(it, SapHanaSourceJdbcStreamStateValue::class.java)
            }
        }
        return when (unsplitPartition) {
            is SapHanaJdbcSplittableSnapshotPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is SapHanaJdbcSplittableSnapshotWithCursorPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is SapHanaJdbcCursorIncrementalPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is SapHanaJdbcUnsplittableSnapshotPartition -> listOf(unsplitPartition)
            is SapHanaJdbcUnsplittableSnapshotWithCursorPartition -> listOf(unsplitPartition)
        }
    }

    private fun SapHanaJdbcSplittableSnapshotPartition.split(
        splitPointValues: List<SapHanaSourceJdbcStreamStateValue>
    ): List<SapHanaJdbcSplittableSnapshotPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            SapHanaJdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                primaryKey = checkpointColumns,
                triggerCdcPartitionState,
                lowerBound,
                upperBound,
            )
        }
    }

    private fun SapHanaJdbcSplittableSnapshotWithCursorPartition.split(
        splitPointValues: List<SapHanaSourceJdbcStreamStateValue>
    ): List<SapHanaJdbcSplittableSnapshotWithCursorPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            SapHanaJdbcSplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                primaryKey = checkpointColumns,
                triggerCdcPartitionState,
                lowerBound,
                upperBound,
                cursor,
                cursorUpperBound,
            )
        }
    }

    private fun SapHanaJdbcCursorIncrementalPartition.split(
        splitPointValues: List<SapHanaSourceJdbcStreamStateValue>
    ): List<SapHanaJdbcCursorIncrementalPartition> {
        val inners: List<JsonNode> = splitPointValues.mapNotNull { it.cursorPair(stream)?.second }
        val lbs: List<JsonNode> = listOf(cursorLowerBound) + inners
        val ubs: List<JsonNode> = inners + listOf(cursorUpperBound)
        return lbs.zip(ubs).mapIndexed { idx: Int, (lowerBound, upperBound) ->
            SapHanaJdbcCursorIncrementalPartition(
                selectQueryGenerator,
                streamState,
                cursor,
                triggerCdcPartitionState,
                lowerBound,
                isLowerBoundIncluded = idx == 0,
                upperBound,
            )
        }
    }
}
