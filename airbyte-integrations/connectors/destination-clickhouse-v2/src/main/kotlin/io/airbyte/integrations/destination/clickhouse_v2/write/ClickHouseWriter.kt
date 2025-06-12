/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendTruncateStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseAirbyteClient
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
class ClickHouseWriter(
    @Named("internalNamespace") private val internalNamespace: String,
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val clickhouseClient: ClickhouseAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        names.values
            .map { (tableNames, _) -> tableNames.finalTableName!!.namespace }
            .forEach { clickhouseClient.createNamespace(it) }
        clickhouseClient.createNamespace(internalNamespace)

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
                DirectLoadTableAppendStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping,
                    clickhouseClient,
                    clickhouseClient,
                    streamStateStore,
                )
            stream.generationId ->
                DirectLoadTableAppendTruncateStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping,
                    clickhouseClient,
                    clickhouseClient,
                    streamStateStore,
                )
            else ->
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - current generation ${stream.generationId}; minimum generation ${stream.minimumGenerationId}"
                )
        }
    }
}
