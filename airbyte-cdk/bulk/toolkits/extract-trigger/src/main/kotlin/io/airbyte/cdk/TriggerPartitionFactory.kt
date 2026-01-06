/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.InvalidCursor
import io.airbyte.cdk.output.InvalidPrimaryKey
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import kotlin.collections.associateWith
import kotlin.collections.find
import kotlin.collections.first
import kotlin.collections.getOrPut
import kotlin.collections.isNotEmpty
import kotlin.collections.map
import kotlin.collections.mapIndexed
import kotlin.collections.mapNotNull
import kotlin.collections.plus
import kotlin.collections.toList
import kotlin.collections.toSet
import kotlin.collections.zip
import kotlin.jvm.java
import kotlin.run
import kotlin.to

@Primary
@Singleton
class TriggerPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val handler: CatalogValidationFailureHandler,
    val selectQueryGenerator: SelectQueryGenerator,
    private val config: TriggerTableConfig,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        TriggerStreamState,
        TriggerPartition,
    > {

    private val streamStates = ConcurrentHashMap<StreamIdentifier, TriggerStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): TriggerStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            TriggerStreamState(sharedState, streamFeedBootstrap)
        }

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): TriggerPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: TriggerStreamState = streamState(streamFeedBootstrap)
        val opaqueStateValue: OpaqueStateValue? = streamFeedBootstrap.currentState

        // An empty table stream state will be marked as a nullNode. This prevents repeated attempt
        // to read it. This relies on the fact that neither cursor columns nor trigger table
        // timestamps can contain nulls, so we won't see a null value from the DB.
        if (opaqueStateValue?.isNull == true) {
            return null
        }

        if (opaqueStateValue == null) {
            return coldStart(streamState)
        }
        val sv: DefaultJdbcStreamStateValue =
            Jsons.treeToValue(opaqueStateValue, DefaultJdbcStreamStateValue::class.java)
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
                TriggerSplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    config,
                    primaryKey = pkMap.keys.toList(),
                    lowerBound = pkMap.values.toList(),
                    upperBound = null,
                )
            }
        } else {
            val (cursor: Field, cursorCheckpoint: JsonNode) = cursorPair
            val triggerCdcPartitionState =
                if (cursor.id == config.CURSOR_FIELD.id) TriggerCdcPartitionState.INCREMENTAL
                else null

            if (!isIncrementalSync) {
                handler.accept(ResetStream(stream.id))
                streamState.reset()
                coldStart(streamState)
            } else if (pkMap.isNotEmpty()) {
                // Snapshot ongoing.
                TriggerSplittableSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    config,
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
                TriggerCursorIncrementalPartition(
                    selectQueryGenerator,
                    streamState,
                    config,
                    cursor,
                    triggerCdcPartitionState,
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
                InvalidPrimaryKey(stream.id, primaryKey.keys.toList()),
            )
            return null
        }
        return fields.associateWith { primaryKey[it.id]!! }
    }

    private fun DefaultJdbcStreamStateValue.cursorPair(stream: Stream): Pair<Field, JsonNode>? {
        if (cursors.size > 1) {
            handler.accept(
                InvalidCursor(stream.id, cursors.keys.toString()),
            )
            return null
        }
        val cursorLabel: String = cursors.keys.first()
        val cursor: FieldOrMetaField? =
            stream.schema.find { it.id == cursorLabel }
                ?: config.COMMON_FIELDS.find { it.id == cursorLabel }
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

    private fun coldStart(streamState: TriggerStreamState): TriggerPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            if (pkChosenFromCatalog.isEmpty()) {
                return TriggerUnsplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    config,
                )
            }
            return TriggerSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                config,
                pkChosenFromCatalog,
                lowerBound = null,
                upperBound = null,
            )
        }
        val cursorChosenFromCatalog: Field =
            stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")
        if (pkChosenFromCatalog.isEmpty()) {
            return TriggerUnsplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog,
                config,
            )
        }
        val triggerCdcPartitionState =
            if (config.cdcEnabled) TriggerCdcPartitionState.SNAPSHOT else null
        return TriggerSplittableSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            config,
            pkChosenFromCatalog,
            triggerCdcPartitionState,
            lowerBound = null,
            upperBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )
    }

    override fun split(
        unsplitPartition: TriggerPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<TriggerPartition> {
        val splitPartitionBoundaries: List<DefaultJdbcStreamStateValue> by lazy {
            opaqueStateValues.map { Jsons.treeToValue(it, DefaultJdbcStreamStateValue::class.java) }
        }
        return when (unsplitPartition) {
            is TriggerSplittableSnapshotPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is TriggerSplittableSnapshotWithCursorPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is TriggerCursorIncrementalPartition -> unsplitPartition.split(splitPartitionBoundaries)
            is TriggerUnsplittableSnapshotPartition -> listOf(unsplitPartition)
            is TriggerUnsplittableSnapshotWithCursorPartition -> listOf(unsplitPartition)
        }
    }

    private fun TriggerSplittableSnapshotPartition.split(
        splitPointValues: List<DefaultJdbcStreamStateValue>
    ): List<TriggerSplittableSnapshotPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            TriggerSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                config,
                primaryKey = checkpointColumns,
                triggerCdcPartitionState,
                lowerBound,
                upperBound,
            )
        }
    }

    private fun TriggerSplittableSnapshotWithCursorPartition.split(
        splitPointValues: List<DefaultJdbcStreamStateValue>
    ): List<TriggerSplittableSnapshotWithCursorPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            TriggerSplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                config,
                primaryKey = checkpointColumns,
                triggerCdcPartitionState,
                lowerBound,
                upperBound,
                cursor,
                cursorUpperBound,
            )
        }
    }

    private fun TriggerCursorIncrementalPartition.split(
        splitPointValues: List<DefaultJdbcStreamStateValue>
    ): List<TriggerCursorIncrementalPartition> {
        val inners: List<JsonNode> = splitPointValues.mapNotNull { it.cursorPair(stream)?.second }
        val lbs: List<JsonNode> = listOf(cursorLowerBound) + inners
        val ubs: List<JsonNode> = inners + listOf(cursorUpperBound)
        return lbs.zip(ubs).mapIndexed { idx: Int, (lowerBound, upperBound) ->
            TriggerCursorIncrementalPartition(
                selectQueryGenerator,
                streamState,
                config,
                cursor,
                triggerCdcPartitionState,
                lowerBound,
                isLowerBoundIncluded = idx == 0,
                upperBound,
            )
        }
    }
}
