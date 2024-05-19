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
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.util.addDefaultNamespaceToStreams
import io.airbyte.integrations.base.destination.operation.DefaultFlush
import io.airbyte.integrations.base.destination.operation.DefaultSyncOperation
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksNamingTransformer
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import io.airbyte.integrations.destination.databricks.operation.DatabricksStorageOperation
import io.airbyte.integrations.destination.databricks.operation.DatabricksStreamOperationFactory
import io.airbyte.integrations.destination.databricks.staging.DatabricksFileBufferFactory
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.DestinationSyncMode
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
        // TODO: Add proper checks for
        //   Check schema permissions, or if raw_override and default already exists
        //   Check catalog permissions to USE catalog
        //   Check CREATE volume, COPY INTO, File upload permissions
        //   Check Table creation, Table drop permissions
        val connectorConfig = DatabricksConnectorConfig.deserialize(config)
        val sqlGenerator =
            DatabricksSqlGenerator(DatabricksNamingTransformer(), connectorConfig.database)
        val datasource = DatabricksConnectorClientsFactory.createDataSource(connectorConfig)
        val jdbcDatabase = DefaultJdbcDatabase(datasource)
        val destinationHandler =
            DatabricksDestinationHandler(connectorConfig.database, jdbcDatabase)
        val workspaceClient =
            DatabricksConnectorClientsFactory.createWorkspaceClient(
                connectorConfig.hostname,
                connectorConfig.authentication
            )
        val storageOperations =
            DatabricksStorageOperation(
                sqlGenerator,
                destinationHandler,
                workspaceClient,
                connectorConfig.database,
                connectorConfig.purgeStagingData
            )
        val dummyNamespace = connectorConfig.rawSchemaOverride
        val dummyName = "airbyte_check_test_table"
        val streamId =
            StreamId(
                dummyNamespace,
                dummyName,
                dummyNamespace,
                dummyName,
                dummyNamespace,
                dummyName
            )

        try {
            storageOperations.prepareStage(streamId, DestinationSyncMode.OVERWRITE)
        } catch (e: Exception) {
            log.error(e) { "Failed to prepare stage as part of CHECK" }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("Failed to prepare stage")
        }

        try {
            val writeBuffer = DatabricksFileBufferFactory.createBuffer(FileUploadFormat.CSV)
            writeBuffer.use {
                it.accept("{\"airbyte_check\":\"passed\"}", "{}", System.currentTimeMillis())
                it.flush()
                storageOperations.writeToStage(streamId, writeBuffer)
            }
        } catch (e: Exception) {
            log.error(e) { "Failed to write to stage as part of CHECK" }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("Failed to write to stage")
        }

        try {
            storageOperations.cleanupStage(streamId)
        } catch (e: Exception) {
            log.error(e) { "Failed to cleanup stage" }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("Failed to cleanup stage")
        }

        return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
    }

    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {

        // TODO: Deserialization should be taken care by connector runner framework later
        val connectorConfig = DatabricksConnectorConfig.deserialize(config)
        // TODO: This abomination continues to stay, this call should be implicit in ParsedCatalog
        //  with defaultNamespace injected
        addDefaultNamespaceToStreams(catalog, connectorConfig.schema)

        val sqlGenerator =
            DatabricksSqlGenerator(DatabricksNamingTransformer(), connectorConfig.database)
        val catalogParser = CatalogParser(sqlGenerator, connectorConfig.rawSchemaOverride)
        val parsedCatalog = catalogParser.parseCatalog(catalog)
        val workspaceClient =
            DatabricksConnectorClientsFactory.createWorkspaceClient(
                connectorConfig.hostname,
                connectorConfig.authentication
            )
        val datasource = DatabricksConnectorClientsFactory.createDataSource(connectorConfig)
        val jdbcDatabase = DefaultJdbcDatabase(datasource)
        val destinationHandler =
            DatabricksDestinationHandler(connectorConfig.database, jdbcDatabase)

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
                connectorConfig.schema,
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
                    (Runtime.getRuntime().maxMemory() * BufferManager.MEMORY_LIMIT_RATIO).toLong(),
                ),
            defaultNamespace = Optional.of(connectorConfig.schema),
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
