/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
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
import io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

/** Top-level orchestrator for Redshift destination syncs */
@Singleton
class RedshiftWriter(
    private val catalog: DestinationCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val redshiftClient: RedshiftAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {

    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        // Create namespaces for all final tables
        val namespaces =
            catalog.streams
                .flatMap { listOfNotNull(it.tableSchema.tableNames.finalTableName?.namespace) }
                .toSet()

        namespaces.forEach { redshiftClient.createNamespace(it) }

        initialStatuses = stateGatherer.gatherInitialStatus()
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val realTableName = stream.tableSchema.tableNames.finalTableName!!
        val tempTableName = tempTableNameGenerator.generate(realTableName)
        val columnNameMapping =
            ColumnNameMapping(stream.tableSchema.columnSchema.inputToFinalColumnNames)
        val useDedupe = stream.tableSchema.importType is Dedupe

        log.info {
            "Creating stream loader for ${realTableName.namespace}.${realTableName.name}: " +
                "mode=${if (useDedupe) "dedupe" else "append"}, " +
                "minGenId=${stream.minimumGenerationId}, genId=${stream.generationId}"
        }

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
                            redshiftClient,
                            redshiftClient,
                            streamStateStore,
                        )
                    else ->
                        DirectLoadTableAppendStreamLoader(
                            stream,
                            initialStatus,
                            realTableName = realTableName,
                            tempTableName = tempTableName,
                            columnNameMapping,
                            redshiftClient,
                            redshiftClient,
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
                            redshiftClient,
                            redshiftClient,
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
                            redshiftClient,
                            redshiftClient,
                            streamStateStore,
                        )
                }
            else ->
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - " +
                        "current generation ${stream.generationId}; " +
                        "minimum generation ${stream.minimumGenerationId}"
                )
        }
    }
}
