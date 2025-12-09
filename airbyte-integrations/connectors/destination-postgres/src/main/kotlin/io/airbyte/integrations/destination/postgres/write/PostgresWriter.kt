/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

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
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
class PostgresWriter(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val postgresClient: PostgresAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
    private val postgresConfiguration: PostgresConfiguration,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        names.values
            .map { (tableNames, _) -> tableNames.finalTableName!!.namespace }
            .forEach { postgresClient.createNamespace(it) }

        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val tableNameInfo = names[stream]!!
        val realTableName = tableNameInfo.tableNames.finalTableName!!
        val tempTableName = tempTableNameGenerator.generate(realTableName)
        val columnNameMapping = tableNameInfo.columnNameMapping

        val isRawTablesMode = postgresConfiguration.legacyRawTablesOnly == true
        if (isRawTablesMode && stream.importType is Dedupe) {
            log.warn { "Dedupe mode is not supported in raw tables mode. Falling back to Append." }
        }
        val useDedupe = !isRawTablesMode && stream.importType is Dedupe

        return when (stream.minimumGenerationId) {
            0L ->
                when {
                    useDedupe ->
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
                when {
                    useDedupe ->
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
