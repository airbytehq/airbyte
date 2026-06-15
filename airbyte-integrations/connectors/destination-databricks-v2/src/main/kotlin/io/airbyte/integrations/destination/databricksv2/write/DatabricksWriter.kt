/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
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
import io.airbyte.integrations.destination.databricksv2.client.DatabricksAirbyteClient
import jakarta.inject.Singleton

@Singleton
class DatabricksWriter(
    private val catalog: DestinationCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val databricksClient: DatabricksAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        catalog.streams
            .map { it.tableSchema.tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { databricksClient.createNamespace(it) }

        initialStatuses = stateGatherer.gatherInitialStatus()
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val realTableName = stream.tableSchema.tableNames.finalTableName!!
        val tempTableName = stream.tableSchema.tableNames.tempTableName!!
        val columnNameMapping =
            ColumnNameMapping(stream.tableSchema.columnSchema.inputToFinalColumnNames)
        val useDedupe = stream.tableSchema.importType is Dedupe

        return when (stream.minimumGenerationId) {
            0L ->
                if (useDedupe) {
                    DirectLoadTableDedupStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        databricksClient,
                        databricksClient,
                        streamStateStore,
                    )
                } else {
                    DirectLoadTableAppendStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        databricksClient,
                        databricksClient,
                        streamStateStore,
                    )
                }
            stream.generationId ->
                if (useDedupe) {
                    DirectLoadTableDedupTruncateStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        databricksClient,
                        databricksClient,
                        streamStateStore,
                        tempTableNameGenerator,
                    )
                } else {
                    DirectLoadTableAppendTruncateStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        databricksClient,
                        databricksClient,
                        streamStateStore,
                    )
                }
            else ->
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - current generation ${stream.generationId}; " +
                        "minimum generation ${stream.minimumGenerationId}",
                )
        }
    }
}
