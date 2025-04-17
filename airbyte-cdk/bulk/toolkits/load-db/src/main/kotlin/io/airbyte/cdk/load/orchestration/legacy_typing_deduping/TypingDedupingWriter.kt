/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.DestinationHandler
import io.airbyte.cdk.load.orchestration.DestinationInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.TableNames
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import java.util.concurrent.Executors
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

class TypingDedupingWriter(
    private val names: Map<DestinationStream, Pair<TableNames, ColumnNameMapping>>,
    private val stateGatherer:
        DestinationInitialStatusGatherer<TypingDedupingDestinationInitialStatus>,
    private val destinationHandler: DestinationHandler,
    private val rawTableOperations: TypingDedupingRawTableOperations,
    private val finalTableOperations: TypingDedupingFinalTableOperations,
    private val disableTypeDedupe: Boolean,
) : DestinationWriter {
    private lateinit var initialStatuses:
        Map<DestinationStream, TypingDedupingDestinationInitialStatus>

    override suspend fun setup() {
        Executors.newFixedThreadPool(4).asCoroutineDispatcher().use { dispatcher ->
            destinationHandler.createNamespaces(
                names.values.map { (tableNames, _) -> tableNames.rawTableName!!.namespace } +
                    names.values.map { (tableNames, _) -> tableNames.finalTableName!!.namespace }
            )

            val initialInitialStatuses:
                Map<DestinationStream, TypingDedupingDestinationInitialStatus> =
                stateGatherer.gatherInitialStatus(names)

            // TODO migrations - we should probably actually drop all existing migrations as part of
            //   this project, but eventually we'll need some solution here

            // If we have a schema mismatch, then execute a soft reset.
            val streamsNeedingSoftReset =
                initialInitialStatuses.filter { (_, status) ->
                    // if the table doesn't exist, then by definition we don't have a schema
                    // mismatch.
                    status.finalTableStatus?.isSchemaMismatch ?: false
                }
            runBlocking(dispatcher) {
                streamsNeedingSoftReset.forEach { (stream, _) ->
                    launch {
                        val (tableNames, columnNameMapping) = names[stream]!!
                        finalTableOperations.softResetFinalTable(
                            stream,
                            tableNames,
                            columnNameMapping
                        )
                    }
                }
            }

            // Soft reset will modify the initial status of a table.
            // Refetch their statuses.
            val statusesAfterSoftReset =
                stateGatherer.gatherInitialStatus(
                    names.filterKeys { streamsNeedingSoftReset.containsKey(it) }
                )
            // second map "wins" when adding two maps together, so we'll retain the newer statuses.
            initialStatuses = initialInitialStatuses + statusesAfterSoftReset
        }
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val (tableNames, columnNameMapping) = names[stream]!!
        return TypingDedupingStreamLoader(
            stream,
            initialStatuses[stream]!!,
            tableNames,
            columnNameMapping,
            rawTableOperations,
            finalTableOperations,
            disableTypeDedupe = disableTypeDedupe,
        )
    }
}
