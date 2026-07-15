/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.schema.model.TableName
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
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.escapeJsonIdentifier
import jakarta.inject.Singleton

@Singleton
class SnowflakeWriter(
    private val catalog: DestinationCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val snowflakeClient: SnowflakeAirbyteClient,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        catalog.streams
            .map { it.tableSchema.tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { snowflakeClient.createNamespace(it) }

        snowflakeClient.createNamespace(
            escapeJsonIdentifier(snowflakeConfiguration.internalTableSchema)
        )

        initialStatuses = stateGatherer.gatherInitialStatus()
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val realTableName = stream.tableSchema.tableNames.finalTableName!!
        val tempTableName = stream.tableSchema.tableNames.tempTableName!!
        val columnNameMapping =
            ColumnNameMapping(stream.tableSchema.columnSchema.inputToFinalColumnNames)
        val generationAwareTableOperationsClient =
            CurrentGenerationTableOperationsClient(snowflakeClient, stream.generationId)
        return when (stream.minimumGenerationId) {
            0L ->
                when (stream.tableSchema.importType) {
                    is Dedupe ->
                        if (!snowflakeConfiguration.legacyRawTablesOnly) {
                            DirectLoadTableDedupStreamLoader(
                                stream,
                                initialStatus,
                                realTableName = realTableName,
                                tempTableName = tempTableName,
                                columnNameMapping,
                                snowflakeClient,
                                snowflakeClient,
                                streamStateStore,
                            )
                        } else {
                            DirectLoadTableAppendStreamLoader(
                                stream,
                                initialStatus,
                                realTableName = realTableName,
                                tempTableName = tempTableName,
                                columnNameMapping,
                                snowflakeClient,
                                snowflakeClient,
                                streamStateStore,
                            )
                        }
                    else ->
                        DirectLoadTableAppendStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            snowflakeClient,
                            snowflakeClient,
                            streamStateStore,
                        )
                }
            stream.generationId ->
                when (stream.tableSchema.importType) {
                    is Dedupe ->
                        if (!snowflakeConfiguration.legacyRawTablesOnly) {
                            DirectLoadTableDedupTruncateStreamLoader(
                                stream,
                                initialStatus,
                                realTableName = realTableName,
                                tempTableName = tempTableName,
                                columnNameMapping,
                                snowflakeClient,
                                generationAwareTableOperationsClient,
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
                                snowflakeClient,
                                generationAwareTableOperationsClient,
                                streamStateStore,
                            )
                        }
                    else ->
                        DirectLoadTableAppendTruncateStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            snowflakeClient,
                            generationAwareTableOperationsClient,
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

@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "kotlin coroutines")
private class CurrentGenerationTableOperationsClient(
    private val delegate: TableOperationsClient,
    private val currentGenerationId: Long,
) : TableOperationsClient by delegate {
    override suspend fun getGenerationId(tableName: TableName): Long =
        delegate.getGenerationId(tableName).takeIf {
            it > 0 && it == currentGenerationId
        } ?: 0
}
