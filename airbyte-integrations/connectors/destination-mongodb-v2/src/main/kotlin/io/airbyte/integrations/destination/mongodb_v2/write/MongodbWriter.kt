/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.write

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
import io.airbyte.integrations.destination.mongodb_v2.client.MongodbAirbyteClient
import jakarta.inject.Singleton

@Singleton
class MongodbWriter(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val mongodbClient: MongodbAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {

    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        // Create all namespaces (databases) - in MongoDB, these are created implicitly
        names.values
            .map { it.tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { mongodbClient.createNamespace(it) }

        // Gather initial status (which collections exist, generation IDs, etc.)
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val tableNames = names[stream]!!.tableNames
        val columnMapping = names[stream]!!.columnNameMapping
        val realTableName = tableNames.finalTableName!!
        val tempTableName = tempTableNameGenerator.generate(realTableName)

        return when (stream.minimumGenerationId) {
            0L -> when (stream.importType) {
                is Dedupe -> DirectLoadTableDedupStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnMapping,
                    mongodbClient,
                    mongodbClient,
                    streamStateStore,
                )
                else -> DirectLoadTableAppendStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnMapping,
                    mongodbClient,
                    mongodbClient,
                    streamStateStore,
                )
            }
            stream.generationId -> when (stream.importType) {
                is Dedupe -> DirectLoadTableDedupTruncateStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnMapping,
                    mongodbClient,
                    mongodbClient,
                    streamStateStore,
                    tempTableNameGenerator,
                )
                else -> DirectLoadTableAppendTruncateStreamLoader(
                    stream,
                    initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnMapping,
                    mongodbClient,
                    mongodbClient,
                    streamStateStore,
                )
            }
            else -> throw SystemErrorException(
                "Cannot execute hybrid refresh - current generation ${stream.generationId}; " +
                "minimum generation ${stream.minimumGenerationId}"
            )
        }
    }
}
