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
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.jdbc.DatabrickStorageOperations
import io.airbyte.integrations.destination.databricks.staging.DatabricksFlushFunction
import io.airbyte.integrations.destination.databricks.staging.DatabricksStagingOperations
import io.airbyte.integrations.destination.databricks.sync.DatabricksStreamOperations
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
        throw UnsupportedOperationException("GetConsumer is not supported, use getSerializedMessageConsumer")
    }

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        TODO()
    }

    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {

        val connectorConfig = DatabricksConnectorConfig.deserialize(config)
        val sqlGenerator = DatabricksSqlGenerator(DatabricksNamingTransformer())
        val catalogParser = CatalogParser(sqlGenerator)
        val parsedCatalog = catalogParser.parseCatalog(catalog)
        val workspaceClient = ConnectorClientsFactory.createWorkspaceClient(connectorConfig.hostname, connectorConfig.apiAuthentication)
        val datasource = ConnectorClientsFactory.createDataSource(connectorConfig)
        val jdbcDatabase = DefaultJdbcDatabase(datasource)
        val destinationHandler = DatabricksDestinationHandler(connectorConfig.database, jdbcDatabase, connectorConfig.rawSchemaOverride)
        val sqlOperations = DatabrickStorageOperations(sqlGenerator, destinationHandler)
        val stagingOperations = DatabricksStagingOperations(workspaceClient)
        val streamOperations = DatabricksStreamOperations(sqlOperations, stagingOperations)
        val syncOperations = DatabricksSyncOperations(parsedCatalog, destinationHandler, streamOperations)

        return AsyncStreamConsumer(
            outputRecordCollector = outputRecordCollector,
            onStart = {syncOperations.initializeStreams()},
            onClose = {_, streamSyncSummaries -> syncOperations.closeStreams(streamSyncSummaries)},
            onFlush = DatabricksFlushFunction(128*1024*1024L),
            catalog = catalog,
            bufferManager = BufferManager(
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
