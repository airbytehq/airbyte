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
import io.airbyte.cdk.source.Field
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
import io.airbyte.cdk.source.select.And
import io.airbyte.cdk.source.select.Equal
import io.airbyte.cdk.source.select.From
import io.airbyte.cdk.source.select.Greater
import io.airbyte.cdk.source.select.LesserOrEqual
import io.airbyte.cdk.source.select.Limit
import io.airbyte.cdk.source.select.NoWhere
import io.airbyte.cdk.source.select.Or
import io.airbyte.cdk.source.select.OrderBy
import io.airbyte.cdk.source.select.SelectColumns
import io.airbyte.cdk.source.select.SelectQuerier
import io.airbyte.cdk.source.select.SelectQuery
import io.airbyte.cdk.source.select.SelectQueryGenerator
import io.airbyte.cdk.source.select.SelectQuerySpec
import io.airbyte.cdk.source.select.Where
import io.airbyte.cdk.source.select.WhereClauseNode
import io.airbyte.cdk.source.select.WhereNode
import io.airbyte.cdk.source.select.optimize
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Default implementation of [Worker] for [ResumableSelectState].
 *
 * Executes a SELECT query with an ORDER BY clause and a LIMIT clause.
 * The ORDER BY ensures that the query is resumable, i.e. current progress can be checkpointed to be resumed in a subsequent query.
 * The LIMIT ensures that the query doesn't run for too long.
 *
 * Note that although the LIMIT value is not checkpointed, it carries over from one [Worker] to the next;
 * where it is increased if the query could have run for a longer period of type and, conversely, is decreased if it ran for too long.
 * This ensures that checkpoints are taken at an appropriate frequency.
 */
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

    val checkpointColumns: List<Field> =
        when (input) {
            is FullRefreshResumableStarting -> input.primaryKey
            is FullRefreshResumableOngoing -> input.primaryKey
            is CursorBasedResumableInitialSyncStarting -> input.primaryKey
            is CursorBasedResumableInitialSyncOngoing -> input.primaryKey
            is CursorBasedIncrementalOngoing -> listOf(input.cursor)
            is CdcResumableInitialSyncStarting -> input.primaryKey
            is CdcResumableInitialSyncOngoing -> input.primaryKey
        }
    val querySpec = SelectQuerySpec(
        SelectColumns(key.fields + checkpointColumns),
        From(key.table),
        input.where(),
        OrderBy(checkpointColumns),
        Limit(input.limit.current)
    )
    val query: SelectQuery = selectQueryGenerator.generate(querySpec.optimize())
    val streamFieldNames: List<String> = key.fields.map { it.id }
    val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory


    override fun call():
        WorkResult<StreamKey, out ResumableSelectState, out SerializableStreamState> {
        var numRecords = 0L
        var lastRecord: ObjectNode? = null
        var stoppedEarly = false
        selectQuerier.executeQuery(query) { record: ObjectNode ->
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

    private fun ResumableSelectState.where(): WhereNode =
        when (this) {
            is CdcResumableInitialSyncStarting -> NoWhere
            is CdcResumableInitialSyncOngoing ->
                Where(pkClause(primaryKey, primaryKeyCheckpoint))
            is CursorBasedResumableInitialSyncStarting ->
                Where(LesserOrEqual(cursor, cursorCheckpoint))
            is CursorBasedResumableInitialSyncOngoing -> {
                val pk = pkClause(primaryKey, primaryKeyCheckpoint)
                val leq = LesserOrEqual(cursor, cursorCheckpoint)
                Where(And(listOf(pk, leq)))
            }
            is CursorBasedIncrementalOngoing -> {
                val gt = Greater(cursor, cursorCheckpoint)
                val leq = LesserOrEqual(cursor, cursorTarget)
                Where(And(listOf(gt, leq)))
            }
            is FullRefreshResumableStarting -> NoWhere
            is FullRefreshResumableOngoing -> Where(pkClause(primaryKey, primaryKeyCheckpoint))
        }

    private fun pkClause(pkCols: List<Field>, pkValues: List<JsonNode>): WhereClauseNode {
        val zipped: List<Pair<Field, JsonNode>> = pkCols.zip(pkValues)
        val disj: List<And> =
            zipped.mapIndexed { idx: Int, (gtCol: Field, gtValue: JsonNode) ->
                val eqs =
                    zipped.take(idx).map { (eqCol: Field, eqValue: JsonNode) ->
                        Equal(eqCol, eqValue)
                    }
                And(eqs + listOf(Greater(gtCol, gtValue)))
            }
        return Or(disj)
    }
}
