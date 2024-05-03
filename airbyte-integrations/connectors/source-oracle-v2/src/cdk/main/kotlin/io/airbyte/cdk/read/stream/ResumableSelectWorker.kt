/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.read.CdcResumableInitialSyncOngoing
import io.airbyte.cdk.read.CdcResumableInitialSyncStarting
import io.airbyte.cdk.read.CursorBasedIncrementalOngoing
import io.airbyte.cdk.read.CursorBasedResumableInitialSyncOngoing
import io.airbyte.cdk.read.CursorBasedResumableInitialSyncStarting
import io.airbyte.cdk.read.DataColumn
import io.airbyte.cdk.read.FullRefreshResumableOngoing
import io.airbyte.cdk.read.FullRefreshResumableStarting
import io.airbyte.cdk.read.LimitState
import io.airbyte.cdk.read.ResumableSelectState
import io.airbyte.cdk.read.SerializableStreamState
import io.airbyte.cdk.read.StreamKey
import io.airbyte.cdk.read.WorkResult
import io.airbyte.cdk.read.Worker
import io.airbyte.cdk.read.completed
import io.airbyte.cdk.read.ongoing
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.concurrent.atomic.AtomicBoolean

class ResumableSelectWorker(
    selectQueryGenerator: SelectQueryGenerator,
    val selectQuerier: SelectQuerier,
    val outputConsumer: OutputConsumer,
    override val input: ResumableSelectState,
) : Worker<StreamKey, ResumableSelectState> {

    private val stopping = AtomicBoolean()

    override fun signalStop() {
        stopping.set(true)
    }

    val dataQueryAst: SelectQueryRootNode = SelectQueryBuilder.selectData(input)
    val dataQuery: SelectQuery = selectQueryGenerator.generateSql(dataQueryAst)
    val streamFieldNames: List<String> = key.dataColumns.map { it.id }
    val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory
    val checkpointColumns: List<DataColumn> =
        when (input) {
            is FullRefreshResumableStarting -> input.primaryKey
            is FullRefreshResumableOngoing -> input.primaryKey
            is CursorBasedResumableInitialSyncStarting -> input.primaryKey
            is CursorBasedResumableInitialSyncOngoing -> input.primaryKey
            is CursorBasedIncrementalOngoing -> listOf(input.cursor)
            is CdcResumableInitialSyncStarting -> input.primaryKey
            is CdcResumableInitialSyncOngoing -> input.primaryKey
        }

    override fun call():
        WorkResult<StreamKey, out ResumableSelectState, out SerializableStreamState> {
        var numRecords = 0L
        var lastRecord: ObjectNode? = null
        var stoppedEarly = false
        selectQuerier.executeQuery(dataQuery) { record: ObjectNode ->
            val dataRecord =
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
            lastRecord = record
            numRecords++
            stoppedEarly = stopping.get()
            return@executeQuery stoppedEarly
        }
        if (!stoppedEarly && numRecords < input.limit.current) {
            return when (input) {
                is FullRefreshResumableStarting -> input.completed(numRecords)
                is FullRefreshResumableOngoing -> input.completed(numRecords)
                is CursorBasedResumableInitialSyncStarting -> input.completed(numRecords)
                is CursorBasedResumableInitialSyncOngoing -> input.completed(numRecords)
                is CursorBasedIncrementalOngoing -> input.completed(numRecords)
                is CdcResumableInitialSyncStarting -> input.completed(numRecords)
                is CdcResumableInitialSyncOngoing -> input.completed(numRecords)
            }
        }
        val checkpointObject: ObjectNode = lastRecord!!
        val checkpointValues: List<JsonNode> =
            checkpointColumns.map { checkpointObject[it.id] ?: nodeFactory.nullNode() }
        val newLimit: LimitState = if (stoppedEarly) input.limit.down() else input.limit.up()
        return when (input) {
            is FullRefreshResumableStarting -> input.ongoing(newLimit, checkpointValues, numRecords)
            is FullRefreshResumableOngoing -> input.ongoing(newLimit, checkpointValues, numRecords)
            is CursorBasedResumableInitialSyncStarting ->
                input.ongoing(newLimit, checkpointValues, numRecords)
            is CursorBasedResumableInitialSyncOngoing ->
                input.ongoing(newLimit, checkpointValues, numRecords)
            is CursorBasedIncrementalOngoing ->
                input.ongoing(newLimit, checkpointValues.first(), numRecords)
            is CdcResumableInitialSyncStarting ->
                input.ongoing(newLimit, checkpointValues, numRecords)
            is CdcResumableInitialSyncOngoing ->
                input.ongoing(newLimit, checkpointValues, numRecords)
        }
    }
}
