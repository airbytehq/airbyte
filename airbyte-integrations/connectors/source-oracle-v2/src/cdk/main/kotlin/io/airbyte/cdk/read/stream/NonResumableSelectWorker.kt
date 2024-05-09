/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.read.CdcNonResumableInitialSyncStarting
import io.airbyte.cdk.read.CursorBasedNonResumableInitialSyncStarting
import io.airbyte.cdk.read.FullRefreshNonResumableStarting
import io.airbyte.cdk.read.NonResumableBackfillState
import io.airbyte.cdk.read.ResumableSelectState
import io.airbyte.cdk.read.SerializableStreamState
import io.airbyte.cdk.read.StreamKey
import io.airbyte.cdk.read.WorkResult
import io.airbyte.cdk.read.Worker
import io.airbyte.cdk.read.completed
import io.airbyte.cdk.source.select.From
import io.airbyte.cdk.source.select.LesserOrEqual
import io.airbyte.cdk.source.select.NoWhere
import io.airbyte.cdk.source.select.SelectColumns
import io.airbyte.cdk.source.select.SelectQuerier
import io.airbyte.cdk.source.select.SelectQuery
import io.airbyte.cdk.source.select.SelectQueryGenerator
import io.airbyte.cdk.source.select.SelectQuerySpec
import io.airbyte.cdk.source.select.Where
import io.airbyte.cdk.source.select.optimize
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.protocol.models.v0.AirbyteRecordMessage

/**
 * Default implementation of [Worker] for [NonResumableBackfillState].
 *
 * Executes a SELECT query with no ORDER BY or LIMIT clauses.
 */
class NonResumableSelectWorker(
    selectQueryGenerator: SelectQueryGenerator,
    val selectQuerier: SelectQuerier,
    val outputConsumer: OutputConsumer,
    override val input: NonResumableBackfillState,
) : Worker<StreamKey, NonResumableBackfillState> {

    override fun signalStop() {} // unstoppable

    val querySpec: SelectQuerySpec = SelectQuerySpec(
        SelectColumns(key.fields),
        From(key.table),
        when (input) {
            is FullRefreshNonResumableStarting -> NoWhere
            is CdcNonResumableInitialSyncStarting -> NoWhere
            is CursorBasedNonResumableInitialSyncStarting ->
                Where(LesserOrEqual(input.cursor, input.cursorCheckpoint))
        }
    )
    val query: SelectQuery = selectQueryGenerator.generate(querySpec.optimize())
    val streamFieldNames: List<String> = key.fields.map { it.id }
    val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory

    override fun call():
        WorkResult<StreamKey, out NonResumableBackfillState, out SerializableStreamState> {
        var numRecords = 0L
        selectQuerier.executeQuery(query) { record: ObjectNode ->
            val dataRecord: ObjectNode =
                nodeFactory.objectNode().apply {
                    for (fieldName in streamFieldNames) {
                        set<JsonNode>(fieldName, record[fieldName] ?: nodeFactory.nullNode())
                    }
                }
            outputConsumer.accept(
                AirbyteRecordMessage()
                    .withStream(key.name)
                    .withNamespace(key.namespace)
                    .withData(dataRecord)
            )
            numRecords++
            return@executeQuery false
        }
        return when (input) {
            is FullRefreshNonResumableStarting -> input.completed(numRecords)
            is CursorBasedNonResumableInitialSyncStarting -> input.completed(numRecords)
            is CdcNonResumableInitialSyncStarting -> input.completed(numRecords)
        }
    }
}
