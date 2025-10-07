/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

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
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.db.escapeJsonIdentifier
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import jakarta.inject.Singleton

@Singleton
class SnowflakeWriter(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val snowflakeClient: SnowflakeAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
    private val snowflakeConfiguration: SnowflakeConfiguration,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        names.values
            .map { (tableNames, _) -> tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { snowflakeClient.createNamespace(it) }

        snowflakeClient.createNamespace(
            escapeJsonIdentifier(snowflakeConfiguration.internalTableSchema)
        )

        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val tableNameInfo = names[stream]!!
        val realTableName = tableNameInfo.tableNames.finalTableName!!
        val tempTableName = tempTableNameGenerator.generate(realTableName)
        val columnNameMapping = tableNameInfo.columnNameMapping
        return when (stream.minimumGenerationId) {
            0L ->
                when (stream.importType) {
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
                when (stream.importType) {
                    is Dedupe ->
                        if (!snowflakeConfiguration.legacyRawTablesOnly) {
                            DirectLoadTableDedupTruncateStreamLoader(
                                stream,
                                initialStatus,
                                realTableName = realTableName,
                                tempTableName = tempTableName,
                                columnNameMapping,
                                snowflakeClient,
                                snowflakeClient,
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
                                snowflakeClient,
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
                            snowflakeClient,
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
