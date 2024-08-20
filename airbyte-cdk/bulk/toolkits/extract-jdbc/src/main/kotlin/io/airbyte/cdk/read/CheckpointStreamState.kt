/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.InvalidCursor
import io.airbyte.cdk.output.InvalidPrimaryKey
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
fun CheckpointStreamState.opaqueStateValue(): OpaqueStateValue =
    when (this) {
        SnapshotCompleted -> DefaultJdbcStreamStateValue.snapshotCompleted
        is SnapshotCheckpoint ->
            DefaultJdbcStreamStateValue.snapshotCheckpoint(primaryKey, primaryKeyCheckpoint)
        is SnapshotWithCursorCheckpoint ->
            DefaultJdbcStreamStateValue.snapshotWithCursorCheckpoint(
                primaryKey,
                primaryKeyCheckpoint,
                cursor,
                cursorUpperBound
            )
        is CursorIncrementalCheckpoint ->
            DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(cursor, cursorCheckpoint)
    }

/**
 * Deserializes a nullable [OpaqueStateValue] into a nullable [CheckpointStreamState] based on the
 * current [JdbcStreamState], which contains the configuration and the catalog.
 */
fun OpaqueStateValue?.checkpoint(
    handler: CatalogValidationFailureHandler,
    streamState: JdbcStreamState<*>,
): CheckpointStreamState? =
    if (this == null) {
        null
    } else {
        Jsons.treeToValue(this, DefaultJdbcStreamStateValue::class.java)
            .checkpoint(handler, streamState)
    }

private fun DefaultJdbcStreamStateValue.checkpoint(
    handler: CatalogValidationFailureHandler,
    streamState: JdbcStreamState<*>,
): CheckpointStreamState? {
    val sharedState: JdbcSharedState = streamState.sharedState
    val stream: Stream = streamState.stream
    val pkMap: Map<Field, JsonNode> = run {
        if (primaryKey.isEmpty()) {
            return@run mapOf()
        }
        val pk: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (primaryKey.keys != pk.map { it.id }.toSet()) {
            handler.accept(
                InvalidPrimaryKey(stream.name, stream.namespace, primaryKey.keys.toList()),
            )
            return null
        }
        pk.associateWith { primaryKey[it.id]!! }
    }
    val cursorPair: Pair<Field, JsonNode>? = run {
        if (cursors.isEmpty()) {
            return@run null
        }
        if (cursors.size > 1) {
            handler.accept(
                InvalidCursor(
                    streamState.stream.name,
                    streamState.stream.namespace,
                    cursors.keys.toString()
                ),
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
        cursor to cursors[cursorLabel]!!
    }
    val isCursorBasedIncremental: Boolean =
        stream.configuredSyncMode == SyncMode.INCREMENTAL && !sharedState.configuration.global

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
