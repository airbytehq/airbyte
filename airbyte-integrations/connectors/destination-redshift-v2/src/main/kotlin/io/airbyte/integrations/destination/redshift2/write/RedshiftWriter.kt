/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write

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
import io.airbyte.integrations.destination.redshift2.client.RedshiftAirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

/**
 * Top-level orchestrator for Redshift destination syncs.
 *
 * Responsibilities:
 * 1. **[setup]**: Creates namespaces (schemas) for all streams and gathers the initial status
 *    (existence/emptiness) of final and temp tables.
 * 2. **[createStreamLoader]**: Selects the appropriate CDK-provided [StreamLoader] for each stream
 *    based on the sync mode (`Append` vs `Dedupe`) and whether a truncate refresh is requested
 *    (`minimumGenerationId == generationId`).
 *
 * The CDK stream loaders manage the full table lifecycle (create, schema evolution, copy/upsert,
 * drop/swap) and store the target table name in [StreamStateStore], which downstream components
 * ([RedshiftAggregateFactory][io.airbyte.integrations.destination.redshift2.dataflow.RedshiftAggregateFactory])
 * read to determine where to load data via S3 staging + COPY.
 */
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
        // Create namespaces for all final and temp table schemas (de-duplicated)
        val namespaces =
            catalog.streams
                .flatMap {
                    listOfNotNull(
                        it.tableSchema.tableNames.finalTableName?.namespace)
                }
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
