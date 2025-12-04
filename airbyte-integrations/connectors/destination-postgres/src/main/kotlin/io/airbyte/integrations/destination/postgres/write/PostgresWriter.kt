/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

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
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import jakarta.inject.Singleton

@Singleton
class PostgresWriter(
    private val catalog: DestinationCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val postgresClient: PostgresAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        catalog.streams
            .map { it.tableSchema.tableNames.finalTableName!!.namespace }
            .forEach { postgresClient.createNamespace(it) }

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
                    is Dedupe ->
                        DirectLoadTableDedupStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            postgresClient,
                            postgresClient,
                            streamStateStore,
                        )
                    else ->
                        DirectLoadTableAppendStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            postgresClient,
                            postgresClient,
                            streamStateStore,
                        )
                }
            stream.generationId ->
                when (stream.importType) {
                    is Dedupe ->
                        DirectLoadTableDedupTruncateStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            postgresClient,
                            postgresClient,
                            streamStateStore,
                            tempTableNameGenerator,
                        )
                    else ->
                        DirectLoadTableAppendTruncateStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            postgresClient,
                            postgresClient,
                            streamStateStore,
                        )
                }
            else ->
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - current generation ${stream.generationId}; minimum generation ${stream.minimumGenerationId}"
                )
        }
    }
}
