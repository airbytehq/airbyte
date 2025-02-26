/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.integrations.destination.mssql.v2.MSSQLContainerHelper.getIpAddress
import io.airbyte.integrations.destination.mssql.v2.MSSQLContainerHelper.getPort
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Files
import java.sql.DriverManager
import org.testcontainers.containers.MSSQLServerContainer
import org.testcontainers.containers.MSSQLServerContainer.MS_SQL_SERVER_PORT
import org.testcontainers.containers.Network

val logger = KotlinLogging.logger {}

private const val BLOB_STORAGE_CREDENTIAL = "MyAzureBlobStorageCredential"
private const val MASTER_ENCRYPTION_PASSWORD = "Ma\$TEr_PA55w0RD!"

/**
 * Helper class for launching/stopping MSSQL Server test containers, as well as updating destination
 * configuration to match test container configuration.
 */
object MSSQLContainerHelper {

    private val network = Network.newNetwork()

    private val testContainer =
        MSSQLServerContainer("mcr.microsoft.com/mssql/server:2022-latest")
            .acceptLicense()
            .withNetwork(network)
            .withLogConsumer { e -> logger.debug { e.utf8String } }

    fun start() {
        synchronized(lock = testContainer) {
            if (!testContainer.isRunning()) {
                testContainer.start()
            }
        }
    }

    fun getHost(): String = testContainer.host

    fun getNetwork(): Network = network

    fun getPassword(): String = testContainer.password

    fun getPort(): Int? = testContainer.getMappedPort(MS_SQL_SERVER_PORT)

    fun getUsername(): String = testContainer.username

    fun getIpAddress(): String? {
        // Ensure that the container is started first
        start()
        return testContainer.containerInfo.networkSettings.networks.entries.first().value.ipAddress
    }

    fun initializeDatabaseForBulkInsert(configFile: String) {
        val config =
            MSSQLConfigUpdater()
                .update(Files.readString(MSSQLTestConfigUtil.getConfigPath(configFile)))
        val accountName = extractConfigValue(configKey = "azure_blob_storage_account_name", config)
        val databaseName = extractConfigValue(configKey = "database", config)
        val dataSourceName = extractConfigValue(configKey = "bulk_load_data_source", config)
        val sharedAccessSignature =
            extractConfigValue(configKey = "shared_access_signature", config)
        val connectionUrl = createDatabaseConnectionUrl()
        val dataSourceLocation = "https://$accountName.blob.core.windows.net"
        DriverManager.getConnection(connectionUrl).use { connection ->
            connection.createStatement().use { statement ->
                statement.execute(
                    """
                            IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '$databaseName')
                            BEGIN
                                CREATE DATABASE [$databaseName];
                            END
                        """.trimIndent()
                )
                statement.execute(
                    """
                            USE [$databaseName];
                            IF NOT EXISTS(SELECT * FROM sys.external_data_sources WHERE name = '$dataSourceName')
                            BEGIN
                                CREATE MASTER KEY ENCRYPTION BY PASSWORD = '$MASTER_ENCRYPTION_PASSWORD';
                                CREATE DATABASE SCOPED CREDENTIAL $BLOB_STORAGE_CREDENTIAL WITH IDENTITY = 'SHARED ACCESS SIGNATURE', SECRET = '$sharedAccessSignature';
                                CREATE EXTERNAL DATA SOURCE $dataSourceName WITH ( TYPE = BLOB_STORAGE, LOCATION = '$dataSourceLocation', CREDENTIAL = $BLOB_STORAGE_CREDENTIAL);
                            END
                        """.trimIndent()
                )
            }
        }
    }

    private fun extractConfigValue(configKey: String, config: String): String {
        val regex = "\"$configKey\"\\s*:\\s*\"([^\"]*)\"".toRegex(RegexOption.MULTILINE)
        val match = regex.find(config)
        return if (match != null) {
            match.groupValues[1]
        } else {
            ""
        }
    }

    private fun createDatabaseConnectionUrl(): String {
        val databaseHost =
            if (System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER") != "docker") {
                "localhost:${getPort()}"
            } else {
                "${getIpAddress()}:$MS_SQL_SERVER_PORT"
            }
        return StringBuilder()
            .apply {
                append("jdbc:sqlserver://$databaseHost")
                append(";encrypt=false;")
                append("user=${getUsername()};password=${getPassword()}")
            }
            .toString()
    }
}

class MSSQLConfigUpdater : ConfigurationUpdater {
    override fun update(config: String): String {
        var updatedConfig = config

        // If not running the connector in docker, we must use the mapped port to connect to the
        // database.  Otherwise, get the container's IP address for the host
        updatedConfig =
            if (System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER") != "docker") {
                getPort()?.let { updatedConfig.replace("$MS_SQL_SERVER_PORT", it.toString()) }
                    ?: updatedConfig
            } else {
                getIpAddress()?.let { config.replace("localhost", it) } ?: updatedConfig
            }

        updatedConfig =
            updatedConfig.replace("replace_me_username", MSSQLContainerHelper.getUsername())
        updatedConfig =
            updatedConfig.replace("replace_me_password", MSSQLContainerHelper.getPassword())
        logger.debug { "Using updated MSSQL configuration: $updatedConfig" }
        return updatedConfig
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(
            config.replace("mssql_default_schema_placeholder", defaultNamespace),
            defaultNamespace
        )
}
