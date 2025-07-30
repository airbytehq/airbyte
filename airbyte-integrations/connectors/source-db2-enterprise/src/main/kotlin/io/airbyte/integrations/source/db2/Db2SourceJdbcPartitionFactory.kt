/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2

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
import io.airbyte.integrations.source.db2.config.Db2SourceConfiguration
import io.airbyte.integrations.source.db2.operations.Db2SourceSelectQueryGenerator
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Primary
@Singleton
class Db2SourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val handler: CatalogValidationFailureHandler,
    val selectQueryGenerator: Db2SourceSelectQueryGenerator,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        Db2JdbcStreamState,
        Db2SourceJdbcPartition,
    > {

    private val streamStates = ConcurrentHashMap<StreamIdentifier, Db2JdbcStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): Db2JdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            Db2JdbcStreamState(sharedState, streamFeedBootstrap)
        }

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): Db2SourceJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: Db2JdbcStreamState = streamState(streamFeedBootstrap)
        val opaqueStateValue: OpaqueStateValue? = streamFeedBootstrap.currentState
        if (opaqueStateValue == null) {
            return coldStart(streamState)
        }
        val sv: Db2SourceStreamStateValue =
            Jsons.treeToValue(opaqueStateValue, Db2SourceStreamStateValue::class.java)
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
                Db2JdbcSplittableSnapshotPartition(
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
                Db2JdbcSplittableSnapshotWithCursorPartition(
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
                Db2JdbcCursorIncrementalPartition(
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

    private fun Db2SourceStreamStateValue.pkMap(stream: Stream): Map<Field, JsonNode>? {
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

    private fun Db2SourceStreamStateValue.cursorPair(stream: Stream): Pair<Field, JsonNode>? {
        if (cursors.size > 1) {
            handler.accept(
                InvalidCursor(stream.id, cursors.keys.toString()),
            )
            return null
        }
        val cursorLabel: String = cursors.keys.first()
        val cursor: FieldOrMetaField? =
            stream.schema.find { it.id == cursorLabel }
                ?: TriggerTableConfig.COMMON_FIELDS.find { it.id == cursorLabel }
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

    private fun coldStart(streamState: Db2JdbcStreamState): Db2SourceJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            if (pkChosenFromCatalog.isEmpty()) {
                return Db2JdbcUnsplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }
            return Db2JdbcSplittableSnapshotPartition(
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
            return Db2JdbcUnsplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog,
            )
        }
        val triggerCdcPartitionState =
            if (configuration.isCdc()) TriggerCdcPartitionState.SNAPSHOT else null
        return Db2JdbcSplittableSnapshotWithCursorPartition(
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

    val configuration: Db2SourceConfiguration = sharedState.configuration as Db2SourceConfiguration

    override fun split(
        unsplitPartition: Db2SourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<Db2SourceJdbcPartition> {
        val splitPartitionBoundaries: List<Db2SourceStreamStateValue> by lazy {
            opaqueStateValues.map { Jsons.treeToValue(it, Db2SourceStreamStateValue::class.java) }
        }
        return when (unsplitPartition) {
            is Db2JdbcSplittableSnapshotPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is Db2JdbcSplittableSnapshotWithCursorPartition ->
                unsplitPartition.split(splitPartitionBoundaries)
            is Db2JdbcCursorIncrementalPartition -> unsplitPartition.split(splitPartitionBoundaries)
            is Db2JdbcUnsplittableSnapshotPartition -> listOf(unsplitPartition)
            is Db2JdbcUnsplittableSnapshotWithCursorPartition -> listOf(unsplitPartition)
        }
    }

    private fun Db2JdbcSplittableSnapshotPartition.split(
        splitPointValues: List<Db2SourceStreamStateValue>
    ): List<Db2JdbcSplittableSnapshotPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            Db2JdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                primaryKey = checkpointColumns,
                triggerCdcPartitionState,
                lowerBound,
                upperBound,
            )
        }
    }

    private fun Db2JdbcSplittableSnapshotWithCursorPartition.split(
        splitPointValues: List<Db2SourceStreamStateValue>
    ): List<Db2JdbcSplittableSnapshotWithCursorPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            Db2JdbcSplittableSnapshotWithCursorPartition(
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

    private fun Db2JdbcCursorIncrementalPartition.split(
        splitPointValues: List<Db2SourceStreamStateValue>
    ): List<Db2JdbcCursorIncrementalPartition> {
        val inners: List<JsonNode> = splitPointValues.mapNotNull { it.cursorPair(stream)?.second }
        val lbs: List<JsonNode> = listOf(cursorLowerBound) + inners
        val ubs: List<JsonNode> = inners + listOf(cursorUpperBound)
        return lbs.zip(ubs).mapIndexed { idx: Int, (lowerBound, upperBound) ->
            Db2JdbcCursorIncrementalPartition(
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
