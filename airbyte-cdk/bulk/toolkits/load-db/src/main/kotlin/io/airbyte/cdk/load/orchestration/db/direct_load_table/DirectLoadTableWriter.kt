/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.direct_load_table

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.load.table.directload.DirectLoadInitialStatus
import io.airbyte.cdk.load.table.directload.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableAppendTruncateStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableDedupStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableDedupTruncateStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore

/**
 * @param directLoadTableTempTableNameMigration Iff you are implementing a destination which
 * previously existed, and used the T+D style of temporary tables (i.e. suffixing the final table
 * with `_airbyte_tmp`), you MUST provide this object.
 */
class DirectLoadTableWriter(
    private val internalNamespace: String,
    private val names: DestinationCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val destinationHandler: DatabaseHandler,
    private val schemaEvolutionClient: TableSchemaEvolutionClient,
    private val tableOperationsClient: TableOperationsClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>
    override suspend fun setup() {
        val namespaces = names.streams.map { it.tableSchema.tableNames.finalTableName!!.namespace }
        destinationHandler.createNamespaces(namespaces + listOf(internalNamespace))

        initialStatuses = stateGatherer.gatherInitialStatus()
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val realTableName = stream.tableSchema.tableNames.finalTableName!!
        val tempTableName = stream.tableSchema.tableNames.tempTableName!!
        val columnNameMapping =
            ColumnNameMapping(stream.tableSchema.columnSchema.inputToFinalColumnNames)
        return when (stream.minimumGenerationId) {
            0L ->
                when (stream.importType) {
                    Append,
                    Overwrite ->
                        DirectLoadTableAppendStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            schemaEvolutionClient,
                            tableOperationsClient,
                            streamStateStore,
                        )
                    is Dedupe ->
                        DirectLoadTableDedupStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            schemaEvolutionClient,
                            tableOperationsClient,
                            streamStateStore,
                        )
                    else -> throw SystemErrorException("Unsupported Sync Mode: $this")
                }
            stream.generationId ->
                when (stream.importType) {
                    Append,
                    Overwrite ->
                        DirectLoadTableAppendTruncateStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            schemaEvolutionClient,
                            tableOperationsClient,
                            streamStateStore,
                        )
                    is Dedupe ->
                        DirectLoadTableDedupTruncateStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            schemaEvolutionClient,
                            tableOperationsClient,
                            streamStateStore,
                            tempTableNameGenerator,
                        )
                    else -> throw SystemErrorException("Unsupported Sync Mode: $this")
                }
            else ->
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - current generation ${stream.generationId}; minimum generation ${stream.minimumGenerationId}"
                )
        }
    }
}
