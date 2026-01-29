/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.write

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.load.table.directload.DirectLoadInitialStatus
import io.airbyte.cdk.load.table.directload.DirectLoadTableAppendTruncateStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableDedupStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableDedupTruncateStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.redshift_v2.client.RedshiftAirbyteClient
import jakarta.inject.Singleton

@Singleton
class RedshiftWriter(
    private val names: DestinationCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val client: RedshiftAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {

    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        // Create all namespaces (both final table and temp table namespaces)
        val namespaces =
            names.streams
                .flatMap { stream ->
                    listOfNotNull(
                        stream.tableSchema.tableNames.finalTableName?.namespace,
                        stream.tableSchema.tableNames.tempTableName?.namespace
                    )
                }
                .toSet()

        namespaces.forEach { client.createNamespace(it) }

        // Gather initial state (which tables exist, generation IDs, etc.)
        initialStatuses = stateGatherer.gatherInitialStatus()
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val realTableName = stream.tableSchema.tableNames.finalTableName!!
        val tempTableName = stream.tableSchema.tableNames.tempTableName!!
        val columnNameMapping =
            ColumnNameMapping(stream.tableSchema.columnSchema.inputToFinalColumnNames)

        // Choose the appropriate stream loader based on import type
        return when (stream.importType) {
            is Dedupe -> {
                // Use DedupTruncateStreamLoader which handles both dedupe and minimumGenerationId
                if (stream.minimumGenerationId > 0) {
                    DirectLoadTableDedupTruncateStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        client,
                        client,
                        streamStateStore,
                        tempTableNameGenerator,
                    )
                } else {
                    DirectLoadTableDedupStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        client,
                        client,
                        streamStateStore,
                    )
                }
            }
            else -> {
                // Use AppendTruncateStreamLoader for append mode which handles minimumGenerationId
                DirectLoadTableAppendTruncateStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping,
                    client,
                    client,
                    streamStateStore,
                )
            }
        }
    }
}
