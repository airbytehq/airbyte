/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.consumers.InvalidCursor
import io.airbyte.cdk.consumers.InvalidPrimaryKey
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.FieldOrMetaField
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.SyncMode

/**
 * [CheckpointStreamState] is the type used to represent state checkpoints for source connectors
 * which make use of this package. This maps to the value of an Airbyte STATE message of type
 * STREAM, interpreted using the provided configuration and configured catalog.
 */
sealed interface CheckpointStreamState

data object SnapshotCompleted : CheckpointStreamState

data class SnapshotCheckpoint(
    val primaryKey: List<Field>,
    val primaryKeyCheckpoint: List<JsonNode>,
) : CheckpointStreamState

data class SnapshotWithCursorCheckpoint(
    val primaryKey: List<Field>,
    val primaryKeyCheckpoint: List<JsonNode>,
    val cursor: Field,
    val cursorUpperBound: JsonNode,
) : CheckpointStreamState

data class CursorIncrementalCheckpoint(
    val cursor: Field,
    val cursorCheckpoint: JsonNode,
) : CheckpointStreamState

/** Serializes a [CheckpointStreamState] into an [OpaqueStateValue]. */
fun CheckpointStreamState.opaqueStateValue(): OpaqueStateValue = Jsons.valueToTree(jsonValue())

private fun CheckpointStreamState.jsonValue(): StreamStateJsonValue =
    when (this) {
        SnapshotCompleted -> StreamStateJsonValue()
        is SnapshotCheckpoint ->
            StreamStateJsonValue(
                primaryKey = primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap(),
            )
        is SnapshotWithCursorCheckpoint ->
            StreamStateJsonValue(
                primaryKey = primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap(),
                cursors = mapOf(cursor.id to cursorUpperBound),
            )
        is CursorIncrementalCheckpoint ->
            StreamStateJsonValue(cursors = mapOf(cursor.id to cursorCheckpoint))
    }

/**
 * Deserializes a nullable [OpaqueStateValue] into a nullable [CheckpointStreamState] based on the
 * current [StreamReadContext], which contains the configuration and the catalog.
 */
fun OpaqueStateValue?.checkpoint(ctx: StreamReadContext): CheckpointStreamState? =
    if (this == null) {
        null
    } else {
        Jsons.treeToValue(this, StreamStateJsonValue::class.java).checkpoint(ctx)
    }

/**
 * [StreamStateJsonValue] is like [CheckpointStreamState] but configuration- and catalog-agnostic.
 * This is the object which is used for de/serializing Airbyte STATE message values from/to
 * [OpaqueStateValue]s.
 */
data class StreamStateJsonValue(
    @JsonProperty("primary_key") val primaryKey: Map<String, JsonNode> = mapOf(),
    @JsonProperty("cursors") val cursors: Map<String, JsonNode> = mapOf(),
)

private fun StreamStateJsonValue.checkpoint(ctx: StreamReadContext): CheckpointStreamState? {
    val pkMap: Map<Field, JsonNode> = run {
        if (primaryKey.isEmpty()) {
            return@run mapOf()
        }
        val keys: List<Field>? =
            ctx.stream.primaryKeyCandidates.find { pk: List<Field> ->
                pk.map { it.id }.toSet() == primaryKey.keys
            }
        if (keys == null) {
            ctx.handler.accept(
                InvalidPrimaryKey(
                    ctx.stream.name,
                    ctx.stream.namespace,
                    primaryKey.keys.toList(),
                ),
            )
            return null
        }
        keys.associateWith { primaryKey[it.id]!! }
    }
    val cursorPair: Pair<Field, JsonNode>? = run {
        if (cursors.isEmpty()) {
            return@run null
        }
        if (cursors.size > 1) {
            ctx.handler.accept(
                InvalidCursor(ctx.stream.name, ctx.stream.namespace, cursors.keys.toString()),
            )
            return null
        }
        val cursorLabel: String = cursors.keys.first()
        val cursor: FieldOrMetaField? = ctx.stream.fields.find { it.id == cursorLabel }
        if (cursor !is Field) {
            ctx.handler.accept(
                InvalidCursor(ctx.stream.name, ctx.stream.namespace, cursorLabel),
            )
            return null
        }
        cursor to cursors[cursorLabel]!!
    }
    val isCursorBasedIncremental: Boolean =
        ctx.stream.configuredSyncMode == SyncMode.INCREMENTAL && !ctx.configuration.global

    return if (cursorPair == null) {
        if (isCursorBasedIncremental) {
            null
        } else if (pkMap.isEmpty()) {
            SnapshotCompleted
        } else {
            SnapshotCheckpoint(pkMap.keys.toList(), pkMap.values.toList())
        }
    } else {
        val (cursor: Field, cursorCheckpoint: JsonNode) = cursorPair
        if (!isCursorBasedIncremental) {
            null
        } else if (pkMap.isEmpty()) {
            CursorIncrementalCheckpoint(cursor, cursorCheckpoint)
        } else {
            SnapshotWithCursorCheckpoint(
                pkMap.keys.toList(),
                pkMap.values.toList(),
                cursor,
                cursorCheckpoint,
            )
        }
    }
}
