/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.GlobalStateValue
import io.airbyte.cdk.command.StreamStateValue
import io.airbyte.cdk.discover.Field

/** Identifies the state of the READ operation for a given [Key]. */
sealed interface State<K : Key> {
    val key: K
}

sealed interface GlobalState : State<GlobalKey>

sealed interface StreamState : State<StreamKey>

/**
 * This subset of states can be worked on by a
 * [io.airbyte.cdk.read.stream.NonResumableSelectWorker].
 */
sealed interface NonResumableBackfillState : StreamState

/**
 * This subset of states can be worked on by a [io.airbyte.cdk.read.stream.ResumableSelectWorker].
 */
sealed interface ResumableSelectState : StreamState {
    val limit: LimitState
}

/** This subset of states can be represented in an Airbyte STATE message. */
sealed interface SerializableState<K : Key> : State<K>

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
) : StreamState, NonResumableBackfillState

data class FullRefreshResumableStarting(
    override val key: StreamKey,
    override val limit: LimitState,
    val primaryKey: List<Field>
) : StreamState, ResumableSelectState

data class FullRefreshResumableOngoing(
    override val key: StreamKey,
    override val limit: LimitState,
    val primaryKey: List<Field>,
    val primaryKeyCheckpoint: List<JsonNode>,
) : StreamState, ResumableSelectState, SerializableStreamState

data class FullRefreshCompleted(
    override val key: StreamKey,
) : StreamState, SerializableStreamState

data class CursorBasedNotStarted(
    override val key: StreamKey,
) : StreamState

data class CursorBasedNonResumableInitialSyncStarting(
    override val key: StreamKey,
    val cursor: Field,
    val cursorCheckpoint: JsonNode,
) : StreamState, NonResumableBackfillState

data class CursorBasedResumableInitialSyncStarting(
    override val key: StreamKey,
    override val limit: LimitState,
    val primaryKey: List<Field>,
    val cursor: Field,
    val cursorCheckpoint: JsonNode,
) : StreamState, ResumableSelectState

data class CursorBasedResumableInitialSyncOngoing(
    override val key: StreamKey,
    override val limit: LimitState,
    val primaryKey: List<Field>,
    val primaryKeyCheckpoint: List<JsonNode>,
    val cursor: Field,
    val cursorCheckpoint: JsonNode,
) : StreamState, ResumableSelectState, SerializableStreamState

data class CursorBasedInitialSyncEmptyCompleted(
    override val key: StreamKey,
) : StreamState, SerializableStreamState

data class CursorBasedIncrementalStarting(
    override val key: StreamKey,
    val cursor: Field,
    val cursorCheckpoint: JsonNode,
) : StreamState

data class CursorBasedIncrementalOngoing(
    override val key: StreamKey,
    override val limit: LimitState,
    val cursor: Field,
    val cursorCheckpoint: JsonNode,
    val cursorTarget: JsonNode,
) : StreamState, ResumableSelectState, SerializableStreamState

data class CursorBasedIncrementalCompleted(
    override val key: StreamKey,
    val cursor: Field,
    val cursorCheckpoint: JsonNode,
) : StreamState, SerializableStreamState

data class CdcInitialSyncNotStarted(
    override val key: StreamKey,
) : StreamState

data class CdcNonResumableInitialSyncStarting(
    override val key: StreamKey,
) : StreamState, NonResumableBackfillState

data class CdcResumableInitialSyncStarting(
    override val key: StreamKey,
    override val limit: LimitState,
    val primaryKey: List<Field>,
) : StreamState, ResumableSelectState

data class CdcResumableInitialSyncOngoing(
    override val key: StreamKey,
    override val limit: LimitState,
    val primaryKey: List<Field>,
    val primaryKeyCheckpoint: List<JsonNode>,
) : StreamState, ResumableSelectState, SerializableStreamState

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
            StreamStateValue(primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap())
        is FullRefreshCompleted -> StreamStateValue()
        is CursorBasedResumableInitialSyncOngoing ->
            StreamStateValue(
                primaryKey = primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap(),
                cursors = mapOf(cursor.id to cursorCheckpoint)
            )
        is CursorBasedInitialSyncEmptyCompleted -> StreamStateValue()
        is CursorBasedIncrementalOngoing ->
            StreamStateValue(cursors = mapOf(cursor.id to cursorCheckpoint))
        is CursorBasedIncrementalCompleted ->
            StreamStateValue(cursors = mapOf(cursor.id to cursorCheckpoint))
        is CdcResumableInitialSyncOngoing ->
            StreamStateValue(primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap())
        is CdcInitialSyncCompleted -> StreamStateValue()
    }

fun CdcNotStarted.completed(checkpoint: GlobalStateValue) =
    WorkResult(this, CdcCompleted(key, checkpoint), 0L)

fun CdcStarting.ongoing(target: GlobalStateValue) =
    WorkResult(this, CdcOngoing(key, checkpoint, target), 0L)

fun CdcOngoing.ongoing(checkpoint: GlobalStateValue, numRecords: Long) =
    WorkResult(this, CdcOngoing(key, checkpoint, target), numRecords)

fun CdcOngoing.completed(numRecords: Long) =
    WorkResult(this, CdcCompleted(key, checkpoint), numRecords)

fun FullRefreshNotStarted.nonResumable() =
    WorkResult(this, FullRefreshNonResumableStarting(key), 0L)

fun FullRefreshNotStarted.resumable(limit: LimitState, primaryKey: List<Field>) =
    WorkResult(this, FullRefreshResumableStarting(key, limit, primaryKey), 0L)

fun FullRefreshNonResumableStarting.completed(numRecords: Long) =
    WorkResult(this, FullRefreshCompleted(key), numRecords)

fun FullRefreshResumableStarting.ongoing(
    limit: LimitState,
    primaryKeyCheckpoint: List<JsonNode>,
    numRecords: Long
) =
    WorkResult(
        this,
        FullRefreshResumableOngoing(key, limit, primaryKey, primaryKeyCheckpoint),
        numRecords
    )

fun FullRefreshResumableStarting.completed(numRecords: Long) =
    WorkResult(this, FullRefreshCompleted(key), numRecords)

fun FullRefreshResumableOngoing.ongoing(
    limit: LimitState,
    primaryKeyCheckpoint: List<JsonNode>,
    numRecords: Long
) =
    WorkResult(
        this,
        FullRefreshResumableOngoing(key, limit, primaryKey, primaryKeyCheckpoint),
        numRecords
    )

fun FullRefreshResumableOngoing.completed(numRecords: Long) =
    WorkResult(this, FullRefreshCompleted(key), numRecords)

fun CursorBasedNotStarted.nonResumable(
    cursor: Field,
    cursorCheckpoint: JsonNode,
) = WorkResult(this, CursorBasedNonResumableInitialSyncStarting(key, cursor, cursorCheckpoint), 0L)

fun CursorBasedNotStarted.resumable(
    limit: LimitState,
    primaryKey: List<Field>,
    cursor: Field,
    cursorCheckpoint: JsonNode,
) =
    WorkResult(
        this,
        CursorBasedResumableInitialSyncStarting(key, limit, primaryKey, cursor, cursorCheckpoint),
        0L
    )

fun CursorBasedNotStarted.completed() =
    WorkResult(this, CursorBasedInitialSyncEmptyCompleted(key), 0L)

fun CursorBasedNonResumableInitialSyncStarting.completed(numRecords: Long) =
    WorkResult(this, CursorBasedIncrementalCompleted(key, cursor, cursorCheckpoint), numRecords)

fun CursorBasedResumableInitialSyncStarting.ongoing(
    limit: LimitState,
    primaryKeyCheckpoint: List<JsonNode>,
    numRecords: Long
) =
    WorkResult(
        this,
        CursorBasedResumableInitialSyncOngoing(
            key,
            limit,
            primaryKey,
            primaryKeyCheckpoint,
            cursor,
            cursorCheckpoint
        ),
        numRecords
    )

fun CursorBasedResumableInitialSyncStarting.completed(numRecords: Long) =
    WorkResult(this, CursorBasedIncrementalCompleted(key, cursor, cursorCheckpoint), numRecords)

fun CursorBasedResumableInitialSyncOngoing.ongoing(
    limit: LimitState,
    primaryKeyCheckpoint: List<JsonNode>,
    numRecords: Long
) =
    WorkResult(
        this,
        CursorBasedResumableInitialSyncOngoing(
            key,
            limit,
            primaryKey,
            primaryKeyCheckpoint,
            cursor,
            cursorCheckpoint
        ),
        numRecords
    )

fun CursorBasedResumableInitialSyncOngoing.completed(numRecords: Long) =
    WorkResult(this, CursorBasedIncrementalCompleted(key, cursor, cursorCheckpoint), numRecords)

fun CursorBasedIncrementalStarting.resumable(limit: LimitState, cursorTarget: JsonNode) =
    WorkResult(
        this,
        CursorBasedIncrementalOngoing(key, limit, cursor, cursorCheckpoint, cursorTarget),
        0L
    )

fun CursorBasedIncrementalOngoing.ongoing(
    limit: LimitState,
    cursorCheckpoint: JsonNode,
    numRecords: Long
) =
    WorkResult(
        this,
        CursorBasedIncrementalOngoing(key, limit, cursor, cursorCheckpoint, cursorTarget),
        numRecords
    )

fun CursorBasedIncrementalOngoing.completed(numRecords: Long) =
    WorkResult(this, CursorBasedIncrementalCompleted(key, cursor, cursorTarget), numRecords)

fun CdcInitialSyncNotStarted.nonResumable() =
    WorkResult(this, CdcNonResumableInitialSyncStarting(key), 0L)

fun CdcInitialSyncNotStarted.resumable(limit: LimitState, primaryKey: List<Field>) =
    WorkResult(this, CdcResumableInitialSyncStarting(key, limit, primaryKey), 0L)

fun CdcNonResumableInitialSyncStarting.completed(numRecords: Long) =
    WorkResult(this, CdcInitialSyncCompleted(key), numRecords)

fun CdcResumableInitialSyncStarting.ongoing(
    limit: LimitState,
    primaryKeyCheckpoint: List<JsonNode>,
    numRecords: Long
) =
    WorkResult(
        this,
        CdcResumableInitialSyncOngoing(key, limit, primaryKey, primaryKeyCheckpoint),
        numRecords
    )

fun CdcResumableInitialSyncStarting.completed(numRecords: Long) =
    WorkResult(this, CdcInitialSyncCompleted(key), numRecords)

fun CdcResumableInitialSyncOngoing.ongoing(
    limit: LimitState,
    primaryKeyCheckpoint: List<JsonNode>,
    numRecords: Long
) =
    WorkResult(
        this,
        CdcResumableInitialSyncOngoing(key, limit, primaryKey, primaryKeyCheckpoint),
        numRecords
    )

fun CdcResumableInitialSyncOngoing.completed(numRecords: Long) =
    WorkResult(this, CdcInitialSyncCompleted(key), numRecords)
