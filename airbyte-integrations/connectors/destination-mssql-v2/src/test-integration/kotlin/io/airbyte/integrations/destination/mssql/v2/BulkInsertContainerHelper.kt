/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import com.azure.storage.blob.BlobContainerClient
import com.azure.storage.blob.BlobServiceClientBuilder
import com.azure.storage.blob.sas.BlobContainerSasPermission
import com.azure.storage.blob.sas.BlobServiceSasSignatureValues
import com.azure.storage.common.StorageSharedKeyCredential
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.integrations.destination.mssql.v2.BulkInsertContainerHelper.getAccountName
import io.airbyte.integrations.destination.mssql.v2.BulkInsertContainerHelper.getAccountUrl
import io.airbyte.integrations.destination.mssql.v2.BulkInsertContainerHelper.getBlobContainer
import io.airbyte.integrations.destination.mssql.v2.BulkInsertContainerHelper.getSharedAccessSignature
import io.airbyte.integrations.destination.mssql.v2.MSSQLContainerHelper.getNetwork
import java.sql.DriverManager
import java.time.OffsetDateTime
import java.util.UUID
import org.testcontainers.azure.AzuriteContainer
import org.testcontainers.containers.MSSQLServerContainer.MS_SQL_SERVER_PORT
import org.testcontainers.containers.Network

private const val BLOB_STORAGE_CREDENTIAL = "MyAzureBlobStorageCredential"
private const val DATA_SOURCE_NAME = "MyAzureBlobStorage"
private const val DATABASE_NAME = "bulkinsert"
private const val MASTER_ENCRYPTION_PASSWORD = "Ma\$TEr_PA55w0RD!"
private const val NETWORK_ALIAS = "blob-storage"
private const val WELL_KNOWN_ACCOUNT_NAME = "devstoreaccount1"
private const val WELL_KNOWN_ACCOUNT_KEY =
    "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="

/**
 * Helper class for launching/stopping the containers required to test bulk insert, as well as
 * updating destination configuration to match test container configuration.
 */
object BulkInsertContainerHelper {

    private lateinit var accountUrl: String
    private lateinit var blobContainer: String
    private lateinit var blobContainerUrl: String
    private lateinit var sharedAccessSignature: String

    private val testContainer =
        AzuriteContainer("mcr.microsoft.com/azure-storage/azurite:3.33.0")
            .withLogConsumer({ e -> logger.debug { e.utf8String } })

    fun start() {
        synchronized(testContainer) {
            // Start the database container first
            MSSQLContainerHelper.start()

            // Start the Azure storage container if not already started
            if (!testContainer.isRunning()) {
                testContainer.withNetwork(getNetwork()).withNetworkAliases(NETWORK_ALIAS).start()

                val sharedKeyCredential =
                    StorageSharedKeyCredential(WELL_KNOWN_ACCOUNT_NAME, WELL_KNOWN_ACCOUNT_KEY)

                val blobServiceClient =
                    BlobServiceClientBuilder()
                        .connectionString(testContainer.connectionString)
                        .credential(sharedKeyCredential)
                        .buildClient()

                val blobContainerClient =
                    blobServiceClient.getBlobContainerClient("test-container-${UUID.randomUUID()}")

                sharedAccessSignature = generateSas(blobContainerClient = blobContainerClient)

                blobContainerClient.createIfNotExists()

                accountUrl = blobServiceClient.accountUrl
                blobContainer = blobContainerClient.blobContainerName ?: ""
                blobContainerUrl = blobContainerClient.blobContainerUrl ?: ""

                prepareDatabaseForBulkInsert()
            }
        }
    }

    fun getAccountName(): String = WELL_KNOWN_ACCOUNT_NAME

    fun getAccountUrl(): String = accountUrl

    fun getBlobContainer(): String = blobContainer

    fun getSharedAccessSignature(): String = sharedAccessSignature

    private fun getBlobContainerUrl(): String = blobContainerUrl

    private fun generateSas(blobContainerClient: BlobContainerClient): String {
        val expiryTime = OffsetDateTime.now().plusDays(2)
        val sasPermission =
            BlobContainerSasPermission()
                .setAddPermission(true)
                .setExecutePermission(true)
                .setCreatePermission(true)
                .setDeletePermission(true)
                .setDeleteVersionPermission(true)
                .setListPermission(true)
                .setReadPermission(true)
                .setWritePermission(true)
        val sasSignatureValues =
            BlobServiceSasSignatureValues(expiryTime, sasPermission)
                .setStartTime(OffsetDateTime.now().minusMinutes(5))

        // Add &comp=list&restype=container to treat the requested resource as a container, not a
        // blob
        return "${blobContainerClient.generateSas(sasSignatureValues)}&comp=list&restype=container"
    }

    private fun prepareDatabaseForBulkInsert() {
        val connectionUrl = createDatabaseConnectionUrl()
        DriverManager.getConnection(connectionUrl).use { connection ->
            connection.createStatement().use { statement ->
                statement.execute("CREATE DATABASE $DATABASE_NAME")
                statement.execute("USE $DATABASE_NAME")
                statement.execute(
                    "CREATE MASTER KEY ENCRYPTION BY PASSWORD = '$MASTER_ENCRYPTION_PASSWORD'",
                )
                statement.execute(
                    "CREATE DATABASE SCOPED CREDENTIAL $BLOB_STORAGE_CREDENTIAL WITH IDENTITY = 'SHARED ACCESS SIGNATURE', SECRET = '${getSharedAccessSignature()}'",
                )
                statement.execute(
                    "CREATE EXTERNAL DATA SOURCE $DATA_SOURCE_NAME WITH ( TYPE = BLOB_STORAGE, LOCATION = '${getBlobContainerUrl().replace("localhost", NETWORK_ALIAS)}', CREDENTIAL = $BLOB_STORAGE_CREDENTIAL)",
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

class BulkInsertConfigUpdater : ConfigurationUpdater {

    private val delegate = MSSQLConfigUpdater()

    override fun update(config: String): String {
        return delegate
            .update(config)
            .replace("replace_me_azure_endpoint", getAccountUrl())
            .replace("replace_me_bulk_data_source", DATA_SOURCE_NAME)
            .replace("replace_me_database_name", DATABASE_NAME)
            .replace("replace_me_azure_account", getAccountName())
            .replace("replace_me_azure_container", getBlobContainer())
            .replace("replace_me_shared_access", getSharedAccessSignature())
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult = delegate.setDefaultNamespace(config, defaultNamespace)
}
