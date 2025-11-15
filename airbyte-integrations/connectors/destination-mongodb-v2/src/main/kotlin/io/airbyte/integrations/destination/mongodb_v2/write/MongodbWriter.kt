/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.write

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
import io.airbyte.integrations.destination.mongodb_v2.client.MongodbClient
import jakarta.inject.Singleton

@Singleton
class MongodbWriter(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val mongodbClient: MongodbClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        names.values
            .map { (tableNames, _) -> tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { mongodbClient.createNamespace(it) }

        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        // Handle case where setup() hasn't been called (e.g., in some tests)
        // Or where stream isn't in the original catalog
        val initialStatus = if (::initialStatuses.isInitialized) {
            initialStatuses[stream] ?: DirectLoadInitialStatus(realTable = null, tempTable = null)
        } else {
            DirectLoadInitialStatus(realTable = null, tempTable = null)
        }

        val tableNameInfo = names[stream]
        val (realTableName, tempTableName, columnNameMapping) = if (tableNameInfo != null) {
            Triple(
                tableNameInfo.tableNames.finalTableName!!,
                tempTableNameGenerator.generate(tableNameInfo.tableNames.finalTableName!!),
                tableNameInfo.columnNameMapping
            )
        } else {
            // Stream not in catalog - create table name dynamically
            val dynamicTableName = io.airbyte.cdk.load.table.TableName(
                namespace = stream.mappedDescriptor.namespace ?: "test",
                name = stream.mappedDescriptor.name
            )
            val dynamicTempTableName = tempTableNameGenerator.generate(dynamicTableName)
            val dynamicColumnMapping = io.airbyte.cdk.load.table.ColumnNameMapping(emptyMap())
            Triple(dynamicTableName, dynamicTempTableName, dynamicColumnMapping)
        }

        // Choose StreamLoader based on sync mode and import type
        return when (stream.minimumGenerationId) {
            0L -> when (stream.importType) {
                is io.airbyte.cdk.load.command.Dedupe ->
                    io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableDedupStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        mongodbClient,
                        mongodbClient,
                        streamStateStore,
                    )
                else ->
                    DirectLoadTableAppendStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        mongodbClient,
                        mongodbClient,
                        streamStateStore,
                    )
            }
            stream.generationId -> when (stream.importType) {
                is io.airbyte.cdk.load.command.Dedupe ->
                    io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableDedupTruncateStreamLoader(
                        stream,
                        initialStatus,
                        realTableName = realTableName,
                        tempTableName = tempTableName,
                        columnNameMapping,
                        mongodbClient,
                        mongodbClient,
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
                        mongodbClient,
                        mongodbClient,
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
