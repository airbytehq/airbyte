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
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksStorageOperations
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import io.airbyte.integrations.destination.databricks.staging.DatabricksFlushFunction
import io.airbyte.integrations.destination.databricks.sync.DatabricksSyncOperations
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Consumer

private val logger = KotlinLogging.logger {}

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
        // TODO: Add checks for
        //   Check schema permissions, or if raw_override and default already exists
        //   Check catalog permissions to USE catalog
        //   Check CREATE volume, COPY INTO, File upload permissions
        //   Check Table creation, Table drop permissions

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
            ConnectorClientsFactory.createWorkspaceClient(
                connectorConfig.hostname,
                connectorConfig.authentication
            )
        val datasource = ConnectorClientsFactory.createDataSource(connectorConfig)
        val jdbcDatabase = DefaultJdbcDatabase(datasource)
        val destinationHandler =
            DatabricksDestinationHandler(connectorConfig.database, jdbcDatabase)

        // Minimum surface area for AsyncConsumer's lifecycle functions to call.
        val storageOperations =
            DatabricksStorageOperations(
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
            DatabricksSyncOperations(
                parsedCatalog,
                destinationHandler,
                connectorConfig.schema,
                storageOperations,
                fileUploadFormat = FileUploadFormat.CSV
            )

        return AsyncStreamConsumer(
            outputRecordCollector = outputRecordCollector,
            onStart = {},
            onClose = { _, streamSyncSummaries ->
                syncOperations.finalizeStreams(streamSyncSummaries)
            },
            onFlush = DatabricksFlushFunction(128 * 1024 * 1024L, syncOperations),
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
    logger.info { "Starting Destination : ${destination.javaClass}" }
    IntegrationRunner(destination).run(args)
    logger.info { "Completed Destination : ${destination.javaClass}" }
}
