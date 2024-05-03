/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.read.CdcInitialSyncNotStarted
import io.airbyte.cdk.read.CursorBasedIncrementalStarting
import io.airbyte.cdk.read.CursorBasedNotStarted
import io.airbyte.cdk.read.DataColumn
import io.airbyte.cdk.read.FullRefreshNotStarted
import io.airbyte.cdk.read.StreamKey
import io.airbyte.cdk.read.StreamState
import io.airbyte.cdk.read.WorkResult
import io.airbyte.cdk.read.Worker
import io.airbyte.cdk.read.completed
import io.airbyte.cdk.read.nonResumable
import io.airbyte.cdk.read.resumable

sealed class PrepWorker<I : StreamState> : Worker<StreamKey, I> {

    override fun signalStop() {} // unstoppable
}

class CdcInitialSyncPrepWorker(
    val config: SourceConfiguration,
    override val input: CdcInitialSyncNotStarted,
) : PrepWorker<CdcInitialSyncNotStarted>() {

    override fun call(): WorkResult<StreamKey, CdcInitialSyncNotStarted, out StreamState> {
        val maybePrimaryKey: List<DataColumn>? =
            key.configuredPrimaryKey ?: key.primaryKeyCandidates.firstOrNull()
        if (maybePrimaryKey != null && config.resumablePreferred) {
            return input.resumable(config.initialLimit, maybePrimaryKey)
        }
        return input.nonResumable()
    }
}

class FullRefreshPrepWorker(
    val config: SourceConfiguration,
    override val input: FullRefreshNotStarted,
) : PrepWorker<FullRefreshNotStarted>() {

    override fun call(): WorkResult<StreamKey, FullRefreshNotStarted, out StreamState> {
        val maybePrimaryKey: List<DataColumn>? =
            key.configuredPrimaryKey ?: key.primaryKeyCandidates.firstOrNull()
        if (maybePrimaryKey != null && config.resumablePreferred) {
            return input.resumable(config.initialLimit, maybePrimaryKey)
        }
        return input.nonResumable()
    }
}

class CursorBasedColdStartWorker(
    val config: SourceConfiguration,
    val selectQueryGenerator: SelectQueryGenerator,
    val selectQuerier: SelectQuerier,
    override val input: CursorBasedNotStarted
) : PrepWorker<CursorBasedNotStarted>() {

    override fun call(): WorkResult<StreamKey, CursorBasedNotStarted, out StreamState> {
        val maybePrimaryKey: List<DataColumn>? =
            key.configuredPrimaryKey ?: key.primaryKeyCandidates.firstOrNull()
        val cursor: DataColumn =
            (key.configuredCursor ?: key.cursorCandidates.firstOrNull()) as? DataColumn
                ?: throw IllegalStateException("Stream has no cursor.")
        val ast: SelectQueryRootNode = SelectQueryBuilder.selectMaxCursorValue(key.table, cursor)
        val q: SelectQuery = selectQueryGenerator.generateSql(ast)
        var maybeRecord: ObjectNode? = null
        selectQuerier.executeQuery(q) { record: ObjectNode ->
            maybeRecord = record
            true
        }
        val record: ObjectNode = maybeRecord ?: return input.completed()
        val checkpointValue: JsonNode = record[cursor.id] ?: NullNode.getInstance()
        if (checkpointValue.isNull) {
            throw IllegalStateException("NULL value found for cursor ${cursor.id}")
        }
        return if (maybePrimaryKey != null && config.resumablePreferred) {
            input.resumable(config.initialLimit, maybePrimaryKey, cursor, checkpointValue)
        } else {
            input.nonResumable(cursor, checkpointValue)
        }
    }
}

class CursorBasedWarmStartWorker(
    val config: SourceConfiguration,
    val selectQueryGenerator: SelectQueryGenerator,
    val selectQuerier: SelectQuerier,
    override val input: CursorBasedIncrementalStarting,
) : PrepWorker<CursorBasedIncrementalStarting>() {

    override fun call(): WorkResult<StreamKey, CursorBasedIncrementalStarting, out StreamState> {
        val ast: SelectQueryRootNode =
            SelectQueryBuilder.selectMaxCursorValue(key.table, input.cursor)
        val q: SelectQuery = selectQueryGenerator.generateSql(ast)
        var maybeRecord: ObjectNode? = null
        selectQuerier.executeQuery(q) { record: ObjectNode ->
            maybeRecord = record
            true
        }
        val record: ObjectNode =
            maybeRecord ?: throw IllegalStateException("Stream has no cursor data")
        val targetValue: JsonNode = record[input.cursor.id] ?: NullNode.getInstance()
        if (targetValue.isNull) {
            throw IllegalStateException("NULL value found for cursor ${input.cursor.id}")
        }
        return input.resumable(config.initialLimit, targetValue)
    }
}
