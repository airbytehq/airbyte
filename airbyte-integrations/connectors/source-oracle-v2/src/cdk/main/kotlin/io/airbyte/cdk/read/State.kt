/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.GlobalStateValue
import io.airbyte.cdk.command.StreamStateValue

/** Identifies the state of the READ operation for a given [Key]. */
sealed interface State<S : Key> {
    val key: S
}

sealed interface GlobalState : State<GlobalKey>

sealed interface StreamState : State<StreamKey>

/** This subset of states can be represented in an Airbyte STATE message. */
sealed interface SerializableState<S : Key> : State<S>

sealed interface SerializableGlobalState : GlobalState, SerializableState<GlobalKey>

sealed interface SerializableStreamState : StreamState, SerializableState<StreamKey>

data class CdcNotStarted(override val key: GlobalKey) : GlobalState

data class CdcStarting(
    override val key: GlobalKey,
    val checkpoint: GlobalStateValue,
) : GlobalState

data class CdcOngoing(
    override val key: GlobalKey,
    val checkpoint: GlobalStateValue,
    val target: GlobalStateValue,
) : GlobalState, SerializableGlobalState

data class CdcCompleted(override val key: GlobalKey, val checkpoint: GlobalStateValue) :
    GlobalState, SerializableGlobalState

data class FullRefreshNotStarted(
    override val key: StreamKey,
) : StreamState

data class FullRefreshNonResumableStarting(
    override val key: StreamKey,
) : StreamState

data class FullRefreshResumableStarting(
    override val key: StreamKey,
    val primaryKey: List<DataColumn>
) : StreamState

data class FullRefreshResumableOngoing(
    override val key: StreamKey,
    val primaryKey: List<DataColumn>,
    val primaryKeyCheckpoint: List<String>,
) : StreamState, SerializableStreamState

data class FullRefreshCompleted(
    override val key: StreamKey,
) : StreamState, SerializableStreamState

data class CursorBasedNotStarted(
    override val key: StreamKey,
) : StreamState

data class CursorBasedInitialSyncStarting(
    override val key: StreamKey,
    val primaryKey: List<DataColumn>,
    val cursor: CursorColumn,
    val cursorCheckpoint: String,
) : StreamState

data class CursorBasedInitialSyncOngoing(
    override val key: StreamKey,
    val primaryKey: List<DataColumn>,
    val primaryKeyCheckpoint: List<String>,
    val cursor: CursorColumn,
    val cursorCheckpoint: String,
) : StreamState, SerializableStreamState

data class CursorBasedIncrementalStarting(
    override val key: StreamKey,
    val cursor: CursorColumn,
    val cursorCheckpoint: String,
) : StreamState

data class CursorBasedIncrementalOngoing(
    override val key: StreamKey,
    val cursor: CursorColumn,
    val cursorCheckpoint: String,
    val cursorTarget: String,
) : StreamState, SerializableStreamState

data class CursorBasedIncrementalCompleted(
    override val key: StreamKey,
    val cursor: CursorColumn,
    val cursorCheckpoint: String,
) : StreamState, SerializableStreamState

data class CdcInitialSyncNotStarted(
    override val key: StreamKey,
) : StreamState

data class CdcInitialSyncStarting(
    override val key: StreamKey,
    val primaryKey: List<DataColumn>,
) : StreamState

data class CdcInitialSyncOngoing(
    override val key: StreamKey,
    val primaryKey: List<DataColumn>,
    val primaryKeyCheckpoint: List<String>,
) : StreamState, SerializableStreamState

data class CdcInitialSyncCompleted(
    override val key: StreamKey,
) : StreamState, SerializableStreamState

fun SerializableGlobalState.toGlobalStateValue(): GlobalStateValue =
    when (this) {
        is CdcOngoing -> this.checkpoint
        is CdcCompleted -> this.checkpoint
    }

fun SerializableStreamState.toStreamStateValue(): StreamStateValue =
    when (this) {
        is FullRefreshResumableOngoing ->
            StreamStateValue(primaryKey.map { it.metadata.label }.zip(primaryKeyCheckpoint).toMap())
        is FullRefreshCompleted -> StreamStateValue()
        is CursorBasedInitialSyncOngoing ->
            StreamStateValue(
                primaryKey = primaryKey.map { it.metadata.label }.zip(primaryKeyCheckpoint).toMap(),
                cursors = mapOf(cursor.name to cursorCheckpoint)
            )
        is CursorBasedIncrementalOngoing ->
            StreamStateValue(cursors = mapOf(cursor.name to cursorCheckpoint))
        is CursorBasedIncrementalCompleted ->
            StreamStateValue(cursors = mapOf(cursor.name to cursorCheckpoint))
        is CdcInitialSyncOngoing ->
            StreamStateValue(primaryKey.map { it.metadata.label }.zip(primaryKeyCheckpoint).toMap())
        is CdcInitialSyncCompleted -> StreamStateValue()
    }
