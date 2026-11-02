/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.table.directload.DirectLoadInitialStatus
import io.airbyte.cdk.load.table.directload.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableAppendTruncateStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.starrocks.client.StarrocksAirbyteClient
import jakarta.inject.Singleton

/**
 * StarRocks [DestinationWriter]. Mirrors `ClickHouseWriter`: creates namespaces, gathers initial
 * table status, and hands out the appropriate direct-load [StreamLoader] per stream.
 *
 * StarRocks deduplicates at LOAD time (`__op` into a PRIMARY KEY table — see the dataflow
 * Aggregate), so even Dedupe streams use the Append-style loaders here: the PRIMARY KEY table is
 * created by the client, and the upsert/delete happens inside Stream Load rather than in a
 * server-side merge.
 */
@Singleton
class StarrocksWriter(
    private val catalog: DestinationCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val starrocksClient: StarrocksAirbyteClient,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        catalog.streams
            .map { stream ->
                requireNotNull(stream.tableSchema.tableNames.finalTableName) {
                        "Stream '${stream.unmappedName}' has no final table name"
                    }
                    .namespace
            }
            .toSet()
            .forEach { starrocksClient.createNamespace(it) }

        initialStatuses = stateGatherer.gatherInitialStatus()
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus =
            requireNotNull(initialStatuses[stream]) {
                "No gathered initial status for stream '${stream.unmappedName}'"
            }
        val realTableName =
            requireNotNull(stream.tableSchema.tableNames.finalTableName) {
                "Stream '${stream.unmappedName}' has no final table name"
            }
        val tempTableName =
            requireNotNull(stream.tableSchema.tableNames.tempTableName) {
                "Stream '${stream.unmappedName}' has no temp table name"
            }
        val columnNameMapping =
            ColumnNameMapping(stream.tableSchema.columnSchema.inputToFinalColumnNames)

        return when (stream.minimumGenerationId) {
            0L ->
                DirectLoadTableAppendStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping,
                    starrocksClient,
                    starrocksClient,
                    streamStateStore,
                )
            stream.generationId ->
                DirectLoadTableAppendTruncateStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping,
                    starrocksClient,
                    starrocksClient,
                    streamStateStore,
                )
            else ->
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - current generation ${stream.generationId}; " +
                        "minimum generation ${stream.minimumGenerationId}",
                )
        }
    }
}
