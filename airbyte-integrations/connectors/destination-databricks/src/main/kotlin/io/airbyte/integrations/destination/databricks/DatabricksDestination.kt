package io.airbyte.integrations.destination.databricks

import com.databricks.client.jdbc.Driver
import com.databricks.sdk.WorkspaceClient
import com.databricks.sdk.core.DatabricksConfig
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
import io.airbyte.integrations.destination.databricks.model.ApiAuthentication
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import io.airbyte.integrations.destination.databricks.model.JdbcAuthentication
import io.airbyte.integrations.destination.databricks.typededupe.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.typededupe.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.sql.DatabricksSqlOperations
import io.airbyte.integrations.destination.databricks.staging.DatabricksFlushFunction
import io.airbyte.integrations.destination.databricks.staging.DatabricksStagingOperations
import io.airbyte.integrations.destination.databricks.sync.DatabricksSyncOperations
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Consumer
import javax.sql.DataSource

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

    private fun createWorkspaceClient(
        hostName: String,
        apiAuthentication: ApiAuthentication
    ): WorkspaceClient {
        return when (apiAuthentication) {
            is ApiAuthentication.PersonalAccessToken -> {
                val config = DatabricksConfig()
                    .setAuthType("pat")
                    .setHost("https://$hostName")
                    .setToken(apiAuthentication.token)
                WorkspaceClient(config)
            }
            is ApiAuthentication.OAuthToken -> TODO("Not yet supported")
        }
    }

    private fun createDataSource(config: DatabricksConnectorConfig): DataSource {
        val className = Driver::class.java.canonicalName
        Class.forName(className)
        val datasource = com.databricks.client.jdbc.DataSource()
        val jdbcUrl =
            "jdbc:databricks://${config.hostname}:${config.port}/default;transportMode=http;httpPath=${config.httpPath}"
        when (config.jdbcAuthentication) {
            is JdbcAuthentication.BasicAuthentication -> {
                datasource.userID = config.jdbcAuthentication.username
                datasource.password = config.jdbcAuthentication.password
                datasource.setURL("$jdbcUrl;AuthMech=3")
            }
            is JdbcAuthentication.OIDCAuthentication -> TODO("Not yet supported")
        }
        return datasource
    }

    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {

        val connectorConfig = DatabricksConnectorConfig.deserialize(config)
        val sqlGenerator = DatabricksSqlGenerator()
        //TODO: add rawNamespace override
        val catalogParser = CatalogParser(sqlGenerator)
        val parsedCatalog = catalogParser.parseCatalog(catalog)
        val workspaceClient = createWorkspaceClient(connectorConfig.hostname, connectorConfig.apiAuthentication)
        val datasource = createDataSource(connectorConfig)
        val jdbcDatabase = DefaultJdbcDatabase(datasource)
        val destinationHandler = DatabricksDestinationHandler(jdbcDatabase)
        val sqlOperations = DatabricksSqlOperations(sqlGenerator, destinationHandler)
        val stagingOperations = DatabricksStagingOperations(workspaceClient)
        val syncOperations = DatabricksSyncOperations(parsedCatalog, destinationHandler)

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
