/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.write

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendTruncateStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableDedupStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableDedupTruncateStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mysql_v2.client.MysqlAirbyteClient
import jakarta.inject.Singleton

/**
 * MySQL implementation of DestinationWriter.
 * Creates appropriate stream loaders based on sync mode and handles initial setup.
 */
@Singleton
class MysqlWriter(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val mysqlClient: MysqlAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    /**
     * Setup: Create all necessary namespaces and gather initial table statuses.
     */
    override suspend fun setup() {
        // Create namespaces for all streams
        names.values
            .map { (tableNames, _) -> tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { mysqlClient.createNamespace(it) }

        // Gather initial status of all tables
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    /**
     * Create a stream loader for the given stream based on sync mode.
     *
     * MySQL supports:
     * - Append mode (minimumGenerationId == 0)
     * - Truncate/Replace mode (minimumGenerationId == generationId)
     * - Dedupe mode for both append and truncate
     */
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val tableNameInfo = names[stream]!!
        val realTableName = tableNameInfo.tableNames.finalTableName!!
        val tempTableName = tempTableNameGenerator.generate(realTableName)
        val columnNameMapping = tableNameInfo.columnNameMapping

        return when (stream.minimumGenerationId) {
            0L ->
                // Append mode: add new records without truncating
                when (stream.importType) {
                    is Dedupe ->
                        DirectLoadTableDedupStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            mysqlClient,
                            mysqlClient,
                            streamStateStore,
                        )
                    else ->
                        DirectLoadTableAppendStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            mysqlClient,
                            mysqlClient,
                            streamStateStore,
                        )
                }
            stream.generationId ->
                // Truncate mode: replace all existing data
                when (stream.importType) {
                    is Dedupe ->
                        DirectLoadTableDedupTruncateStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            mysqlClient,
                            mysqlClient,
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
                            mysqlClient,
                            mysqlClient,
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
