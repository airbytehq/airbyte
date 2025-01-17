/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.integrations.base.destination.operation.DefaultFlush
import io.airbyte.integrations.base.destination.operation.DefaultSyncOperation
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksNamingTransformer
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import io.airbyte.integrations.destination.databricks.operation.DatabricksStorageOperation
import io.airbyte.integrations.destination.databricks.operation.DatabricksStreamOperation
import io.airbyte.integrations.destination.databricks.operation.DatabricksStreamOperationFactory
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Consumer

private val log = KotlinLogging.logger {}

class DatabricksDestination : BaseConnector(), Destination {
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        throw UnsupportedOperationException(
            "GetConsumer is not supported, use getSerializedMessageConsumer"
        )
    }

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        try {
            val connectorConfig = DatabricksConnectorConfig.deserialize(config)
            val datasource = DatabricksConnectorClientsFactory.createDataSource(connectorConfig)
            val sqlGenerator =
                DatabricksSqlGenerator(DatabricksNamingTransformer(), connectorConfig.database, connectorConfig.useVariantDatatype)
            val jdbcDatabase = DefaultJdbcDatabase(datasource)
            val destinationHandler =
                DatabricksDestinationHandler(sqlGenerator, connectorConfig.database, jdbcDatabase)
            val workspaceClient =
                DatabricksConnectorClientsFactory.createWorkspaceClient(
                    connectorConfig.hostname,
                    connectorConfig.authentication
                )
            val storageOperation =
                DatabricksStorageOperation(
                    sqlGenerator,
                    destinationHandler,
                    workspaceClient,
                    connectorConfig.database,
                    connectorConfig.purgeStagingData
                )
            val rawTableNamespace = connectorConfig.rawSchemaOverride
            val finalTableName = "airbyte_check_test_table"

            // Both raw & final Namespaces are same for dummy sync since we don't do any final table
            // operations
            // in check
            val streamId =
                sqlGenerator.buildStreamId(rawTableNamespace, finalTableName, rawTableNamespace)
            val streamConfig =
                StreamConfig(
                    id = streamId,
                    postImportAction = ImportType.APPEND,
                    primaryKey = listOf(),
                    cursor = Optional.empty(),
                    columns = linkedMapOf(),
                    generationId = 1,
                    minimumGenerationId = 1,
                    syncId = 0
                )

            // quick utility method to drop the airbyte_check_test_table table
            // returns a connection status if there was an error, or null on success
            fun dropCheckTable(): AirbyteConnectionStatus? {
                val dropCheckTableStatement =
                    "DROP TABLE IF EXISTS `${connectorConfig.database}`.`${streamId.rawNamespace}`.`${streamId.rawName}`;"
                try {
                    destinationHandler.execute(
                        Sql.of(
                            dropCheckTableStatement,
                        ),
                    )
                } catch (e: Exception) {
                    log.error(e) { "Failed to execute query $dropCheckTableStatement" }
                    return AirbyteConnectionStatus()
                        .withStatus(AirbyteConnectionStatus.Status.FAILED)
                        .withMessage("Failed to execute $dropCheckTableStatement: ${e.message}")
                }
                return null
            }

            // None of the fields in destination initial status matter
            // for a dummy sync with type-dedupe disabled. We only look at these
            // when we perform final table related setup operations.
            // We just need the streamId to perform the calls in streamOperation.
            val initialStatus =
                DestinationInitialStatus(
                    streamConfig = streamConfig,
                    isFinalTablePresent = false,
                    initialRawTableStatus =
                        InitialRawTableStatus(
                            rawTableExists = false,
                            hasUnprocessedRecords = true,
                            maxProcessedTimestamp = Optional.empty()
                        ),
                    initialTempRawTableStatus =
                        InitialRawTableStatus(
                            rawTableExists = false,
                            hasUnprocessedRecords = true,
                            maxProcessedTimestamp = Optional.empty()
                        ),
                    isSchemaMismatch = true,
                    isFinalTableEmpty = true,
                    destinationState = MinimumDestinationState.Impl(needsSoftReset = false),
                    finalTableGenerationId = null,
                    finalTempTableGenerationId = null,
                )

            // We simulate a mini-sync to see the raw table code path is exercised. and disable T+D
            // This code is similar to Snowflake's Check
            destinationHandler.createNamespaces(setOf(rawTableNamespace))
            // Before we start, clean up any preexisting check table from a previous attempt.
            // Even though we clean up at the end. This exists because some version of the old
            // connector
            // didn't clean up properly and to let them pass the check we do it both before and
            // after.
            dropCheckTable()?.let {
                return it
            }
            val streamOperation =
                DatabricksStreamOperation(
                    storageOperation,
                    initialStatus,
                    FileUploadFormat.CSV,
                    disableTypeDedupe = true
                )

            val data =
                """
                {"airbyte_check": "passed"}
                """.trimIndent()
            val message =
                PartialAirbyteMessage()
                    .withSerialized(data)
                    .withRecord(
                        PartialAirbyteRecordMessage()
                            .withEmittedAt(System.currentTimeMillis())
                            .withMeta(
                                AirbyteRecordMessageMeta(),
                            ),
                    )

            streamOperation.writeRecords(streamConfig, listOf(message).stream())
            streamOperation.finalizeTable(
                streamConfig,
                StreamSyncSummary(1, AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE)
            )
            // Clean up after ourselves.
            // Not _strictly_ necessary since we do this at the start of `check`,
            // but it's slightly nicer.
            dropCheckTable()?.let {
                return it
            }
            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (e: Exception) {
            log.error(e) { "Failed to execute check" }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("${e.message}")
        }
    }

    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {

        val connectorConfig = DatabricksConnectorConfig.deserialize(config)

        val sqlGenerator =
            DatabricksSqlGenerator(DatabricksNamingTransformer(), connectorConfig.database, connectorConfig.useVariantDatatype)
        val defaultNamespace = connectorConfig.schema
        val catalogParser =
            CatalogParser(sqlGenerator, defaultNamespace, connectorConfig.rawSchemaOverride)
        val parsedCatalog = catalogParser.parseCatalog(catalog)
        val workspaceClient =
            DatabricksConnectorClientsFactory.createWorkspaceClient(
                connectorConfig.hostname,
                connectorConfig.authentication
            )
        val datasource = DatabricksConnectorClientsFactory.createDataSource(connectorConfig)
        val jdbcDatabase = DefaultJdbcDatabase(datasource)
        val destinationHandler =
            DatabricksDestinationHandler(sqlGenerator, connectorConfig.database, jdbcDatabase)

        // Minimum surface area for AsyncConsumer's lifecycle functions to call.
        val storageOperations =
            DatabricksStorageOperation(
                sqlGenerator,
                destinationHandler,
                workspaceClient,
                connectorConfig.database,
                connectorConfig.purgeStagingData
            )

        // Initialize streams on connector instantiation. Fail fast even before buffers are created
        // if something goes wrong here.
        // Rather than trying to safeguard if succeeded in AutoCloseable's onClose
        val syncOperations =
            DefaultSyncOperation(
                parsedCatalog,
                destinationHandler,
                defaultNamespace,
                DatabricksStreamOperationFactory(storageOperations),
                listOf()
            )

        return AsyncStreamConsumer(
            outputRecordCollector = outputRecordCollector,
            onStart = {},
            onClose = { _, streamSyncSummaries ->
                syncOperations.finalizeStreams(streamSyncSummaries)
            },
            onFlush = DefaultFlush(128 * 1024 * 1024L, syncOperations),
            catalog = catalog,
            bufferManager =
                BufferManager(
                    defaultNamespace = defaultNamespace,
                    (Runtime.getRuntime().maxMemory() * BufferManager.MEMORY_LIMIT_RATIO).toLong(),
                ),
            airbyteMessageDeserializer = AirbyteMessageDeserializer(),
        )
    }

    override val isV2Destination: Boolean
        get() = true
}

fun main(args: Array<String>) {
    val destination = DatabricksDestination()
    log.info { "Starting Destination : ${destination.javaClass}" }
    IntegrationRunner(destination).run(args)
    log.info { "Completed Destination : ${destination.javaClass}" }
}
