package io.airbyte.integrations.destination.mysql.write

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
import io.airbyte.integrations.destination.mysql.client.MySQLAirbyteClient
import jakarta.inject.Singleton

@Singleton
class MySQLWriter(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val client: MySQLAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {

    private var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>? = null

    override suspend fun setup() {
        // Create all namespaces
        names.values
            .map { (tableNames, _) -> tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { client.createNamespace(it) }

        // Gather initial state
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        // Initialize on-demand if setup() wasn't called (e.g., in component tests)
        if (initialStatuses == null) {
            kotlinx.coroutines.runBlocking {
                initialStatuses = stateGatherer.gatherInitialStatus(names)
            }
        }

        val statuses = initialStatuses!!
        val initialStatus = statuses[stream]
            ?: throw IllegalStateException("Stream not found in catalog")

        val tableNameInfo = names[stream]
            ?: throw IllegalStateException("Table name info not found for stream")

        val realTableName = tableNameInfo.tableNames.finalTableName!!
        val tempTableName = tempTableNameGenerator.generate(realTableName)
        val columnNameMapping = tableNameInfo.columnNameMapping

        return when (stream.minimumGenerationId) {
            0L -> when (stream.importType) {
                is io.airbyte.cdk.load.command.Dedupe -> DirectLoadTableDedupStreamLoader(
                    stream,
                    initialStatus,
                    realTableName,
                    tempTableName,
                    columnNameMapping,
                    client,  // TableOperationsClient
                    client,  // TableSchemaEvolutionClient
                    streamStateStore,
                )
                else -> DirectLoadTableAppendStreamLoader(
                    stream,
                    initialStatus,
                    realTableName,
                    tempTableName,
                    columnNameMapping,
                    client,  // TableOperationsClient
                    client,  // TableSchemaEvolutionClient
                    streamStateStore,
                )
            }
            stream.generationId -> when (stream.importType) {
                is io.airbyte.cdk.load.command.Dedupe -> DirectLoadTableDedupTruncateStreamLoader(
                    stream,
                    initialStatus,
                    realTableName,
                    tempTableName,
                    columnNameMapping,
                    client,  // TableOperationsClient
                    client,  // TableSchemaEvolutionClient
                    streamStateStore,
                    tempTableNameGenerator,
                )
                else -> DirectLoadTableAppendTruncateStreamLoader(
                    stream,
                    initialStatus,
                    realTableName,
                    tempTableName,
                    columnNameMapping,
                    client,  // TableOperationsClient
                    client,  // TableSchemaEvolutionClient
                    streamStateStore,
                )
            }
            else -> throw io.airbyte.cdk.SystemErrorException(
                "Hybrid refresh not supported - current generation ${stream.generationId}, minimum ${stream.minimumGenerationId}"
            )
        }
    }
}
