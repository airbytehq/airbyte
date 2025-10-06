/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore

/**
 * @param directLoadTableTempTableNameMigration Iff you are implementing a destination which
 * previously existed, and used the T+D style of temporary tables (i.e. suffixing the final table
 * with `_airbyte_tmp`), you MUST provide this object.
 */
class DirectLoadTableWriter(
    private val internalNamespace: String,
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val destinationHandler: DatabaseHandler,
    private val nativeTableOperations: DirectLoadTableNativeOperations,
    private val sqlTableOperations: DirectLoadTableSqlOperations,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>
    override suspend fun setup() {
        val namespaces =
            names.values.map { (tableNames, _) -> tableNames.finalTableName!!.namespace }.toSet()
        destinationHandler.createNamespaces(namespaces + listOf(internalNamespace))

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
                    Append,
                    Overwrite ->
                        DirectLoadTableAppendStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            nativeTableOperations,
                            sqlTableOperations,
                            streamStateStore,
                        )
                    is Dedupe ->
                        DirectLoadTableDedupStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            nativeTableOperations,
                            sqlTableOperations,
                            streamStateStore,
                        )
                    else -> throw SystemErrorException("Unsupported Sync Mode: $this")
                }
            stream.generationId ->
                when (stream.importType) {
                    Append,
                    Overwrite ->
                        DirectLoadTableAppendTruncateStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            nativeTableOperations,
                            sqlTableOperations,
                            streamStateStore,
                        )
                    is Dedupe ->
                        DirectLoadTableDedupTruncateStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            nativeTableOperations,
                            sqlTableOperations,
                            streamStateStore,
                            tempTableNameGenerator,
                        )
                    else -> throw SystemErrorException("Unsupported Sync Mode: $this")
                }
            else ->
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - current generation ${stream.generationId}; minimum generation ${stream.minimumGenerationId}"
                )
        }
    }
}
