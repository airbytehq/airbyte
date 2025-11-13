/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import java.util.concurrent.Executors
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

class TypingDedupingWriter(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<TypingDedupingDatabaseInitialStatus>,
    private val databaseHandler: DatabaseHandler,
    private val rawTableOperations: TypingDedupingRawTableOperations,
    private val finalTableOperations: TypingDedupingFinalTableOperations,
    private val disableTypeDedupe: Boolean,
    private val streamStateStore: StreamStateStore<TypingDedupingExecutionConfig>,
) : DestinationWriter {
    private lateinit var initialStatuses:
        Map<DestinationStream, TypingDedupingDatabaseInitialStatus>

    override suspend fun setup() {
        Executors.newFixedThreadPool(10).asCoroutineDispatcher().use { dispatcher ->
            val namespaces =
                names.values.map { (tableNames, _) -> tableNames.rawTableName!!.namespace } +
                    names.values.map { (tableNames, _) -> tableNames.finalTableName!!.namespace }
            databaseHandler.createNamespaces(namespaces.toSet())

            val initialInitialStatuses:
                Map<DestinationStream, TypingDedupingDatabaseInitialStatus> =
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
                    TableCatalog(names.filterKeys { streamsNeedingSoftReset.containsKey(it) })
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
            streamStateStore,
        )
    }
}
