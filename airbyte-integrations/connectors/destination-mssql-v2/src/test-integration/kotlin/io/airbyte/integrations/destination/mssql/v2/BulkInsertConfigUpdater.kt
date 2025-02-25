/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import java.sql.DriverManager
import org.testcontainers.containers.MSSQLServerContainer.MS_SQL_SERVER_PORT

private const val BLOB_STORAGE_CREDENTIAL = "MyAzureBlobStorageCredential"
private const val MASTER_ENCRYPTION_PASSWORD = "Ma\$TEr_PA55w0RD!"

class BulkInsertConfigUpdater : ConfigurationUpdater {

    private val delegate = MSSQLConfigUpdater()

    override fun update(config: String): String {
        val updatedConfig = delegate.update(config)
        prepareDatabaseForBulkInsert(
            accountName =
                extractConfigValue(configKey = "azure_blob_storage_account_name", updatedConfig),
            databaseName = extractConfigValue(configKey = "database", updatedConfig),
            dataSourceName = extractConfigValue(configKey = "bulk_load_data_source", updatedConfig),
            sharedAccessSignature =
                extractConfigValue(configKey = "shared_access_signature", updatedConfig),
        )
        return updatedConfig
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult = delegate.setDefaultNamespace(config, defaultNamespace)

    private fun extractConfigValue(configKey: String, config: String): String {
        val regex = "\"$configKey\"\\s*:\\s*\"([^\"]*)\"".toRegex(RegexOption.MULTILINE)
        val match = regex.find(config)
        return if (match != null) {
            match.groupValues[1]
        } else {
            ""
        }
    }

    private fun prepareDatabaseForBulkInsert(
        accountName: String,
        databaseName: String,
        dataSourceName: String,
        sharedAccessSignature: String
    ) {
        val connectionUrl = createDatabaseConnectionUrl()
        val dataSourceLocation = "https://$accountName.blob.core.windows.net"
        DriverManager.getConnection(connectionUrl).use { connection ->
            connection.createStatement().use { statement ->
                statement.execute("CREATE DATABASE [$databaseName]")
                statement.execute("USE [$databaseName]")
                statement.execute(
                    "CREATE MASTER KEY ENCRYPTION BY PASSWORD = '$MASTER_ENCRYPTION_PASSWORD'"
                )
                statement.execute(
                    "CREATE DATABASE SCOPED CREDENTIAL $BLOB_STORAGE_CREDENTIAL WITH IDENTITY = 'SHARED ACCESS SIGNATURE', SECRET = '$sharedAccessSignature'"
                )
                statement.execute(
                    "CREATE EXTERNAL DATA SOURCE $dataSourceName WITH ( TYPE = BLOB_STORAGE, LOCATION = '$dataSourceLocation', CREDENTIAL = $BLOB_STORAGE_CREDENTIAL)"
                )
            }
        }
    }

    private fun createDatabaseConnectionUrl(): String {
        val databaseHost =
            if (System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER") != "docker") {
                "localhost:${MSSQLContainerHelper.getPort()}"
            } else {
                "${MSSQLContainerHelper.getIpAddress()}:$MS_SQL_SERVER_PORT"
            }
        return StringBuilder()
            .apply {
                append("jdbc:sqlserver://$databaseHost")
                append(";encrypt=false;")
                append(
                    "user=${MSSQLContainerHelper.getUsername()};password=${MSSQLContainerHelper.getPassword()}"
                )
            }
            .toString()
    }
}
