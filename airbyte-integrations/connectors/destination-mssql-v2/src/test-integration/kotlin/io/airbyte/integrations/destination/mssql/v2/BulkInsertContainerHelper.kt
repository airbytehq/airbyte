/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import com.azure.storage.blob.BlobServiceClient
import com.azure.storage.blob.BlobServiceClientBuilder
import com.azure.storage.common.StorageSharedKeyCredential
import com.azure.storage.common.sas.AccountSasPermission
import com.azure.storage.common.sas.AccountSasResourceType
import com.azure.storage.common.sas.AccountSasService
import com.azure.storage.common.sas.AccountSasSignatureValues
import com.azure.storage.common.sas.SasIpRange
import com.azure.storage.common.sas.SasProtocol
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.integrations.destination.mssql.v2.BulkInsertContainerHelper.getAccountName
import io.airbyte.integrations.destination.mssql.v2.BulkInsertContainerHelper.getAccountUrl
import io.airbyte.integrations.destination.mssql.v2.BulkInsertContainerHelper.getBlobContainer
import io.airbyte.integrations.destination.mssql.v2.BulkInsertContainerHelper.getSharedAccessSignature
import io.airbyte.integrations.destination.mssql.v2.MSSQLContainerHelper.getNetwork
import java.io.File
import java.sql.DriverManager
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.UUID
import org.testcontainers.azure.AzuriteContainer
import org.testcontainers.containers.MSSQLServerContainer.MS_SQL_SERVER_PORT
import org.testcontainers.containers.NginxContainer
import org.testcontainers.utility.MountableFile

private const val BLOB_STORAGE_CREDENTIAL = "MyAzureBlobStorageCredential"
private const val BLOB_STORAGE_PORT = 10000
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
            .withLogConsumer { e -> logger.debug { e.utf8String } }

    fun start() {
        synchronized(testContainer) {
            // Start the database container first
            MSSQLContainerHelper.start()

            // Start the Azure storage container if not already started
            if (!testContainer.isRunning()) {
                testContainer
                    .withNetwork(getNetwork())
                    .withNetworkAliases(NETWORK_ALIAS)
                    .withNetworkMode(getNetwork().id)
                    .start()

                val sharedKeyCredential =
                    StorageSharedKeyCredential(WELL_KNOWN_ACCOUNT_NAME, WELL_KNOWN_ACCOUNT_KEY)

                val blobServiceClient =
                    BlobServiceClientBuilder()
                        .connectionString(testContainer.connectionString)
                        .credential(sharedKeyCredential)
                        .buildClient()

                val blobContainerClient =
                    blobServiceClient.getBlobContainerClient("test-container-${UUID.randomUUID()}")

                blobContainerClient.createIfNotExists()

                accountUrl = blobServiceClient.accountUrl
                blobContainer = blobContainerClient.blobContainerName ?: ""
                blobContainerUrl = blobContainerClient.blobContainerUrl ?: ""
                sharedAccessSignature = generateAccountSas(blobServiceClient)

                // Set up a nginx proxy to map the public Azure blob storage URL to the container
                createProxyForBlobStorage()

                // Create the external data source for the bulk insert
                prepareDatabaseForBulkInsert()
            }
        }
    }

    fun getAccountName(): String = WELL_KNOWN_ACCOUNT_NAME

    fun getAccountUrl(): String = accountUrl

    fun getBlobContainer(): String = blobContainer

    fun getSharedAccessSignature(): String = sharedAccessSignature

    private fun generateAccountSas(blobServiceClient: BlobServiceClient): String {
        val expiryTime = OffsetDateTime.now(ZoneOffset.UTC).plusDays(5)
        val accountSasPermission =
            AccountSasPermission()
                .setAddPermission(true)
                .setCreatePermission(true)
                .setDeletePermission(true)
                .setDeleteVersionPermission(true)
                .setListPermission(true)
                .setReadPermission(true)
                .setWritePermission(true)
        val accountSasService =
            AccountSasService().setBlobAccess(true).setFileAccess(true).setTableAccess(true)
        val accountSasResourceType =
            AccountSasResourceType().setService(true).setContainer(true).setObject(true)

        val accountSasSignatureValues =
            AccountSasSignatureValues(
                    expiryTime,
                    accountSasPermission,
                    accountSasService,
                    accountSasResourceType,
                )
                .setStartTime(OffsetDateTime.now(ZoneOffset.UTC).minusDays(5))
                .setProtocol(SasProtocol.HTTPS_HTTP)
                .setSasIpRange(SasIpRange().setIpMax("0.0.0.0").setIpMax("255.255.255.255"))

        return blobServiceClient.generateAccountSas(accountSasSignatureValues)
    }

    private fun createProxyForBlobStorage() {
        val proxyPassUrl =
            "http://$NETWORK_ALIAS:$BLOB_STORAGE_PORT/$WELL_KNOWN_ACCOUNT_NAME\$uri\$is_args\$args"
        val nginxConf = File.createTempFile("nginx", ".tmp")
        nginxConf.writeText(
            """
                    events {}
                    http {
                        server {
                            listen       80;
                            resolver     127.0.0.11;
                            location ~ ^/ {
                                proxy_pass $proxyPassUrl;
                                proxy_pass_request_headers      on;
                            }
                        }
                    }
                """.trimIndent(),
        )

        val nginx =
            NginxContainer("nginx:1.27.4")
                .withExposedPorts(80)
                .withNetwork(getNetwork())
                .withNetworkAliases("$WELL_KNOWN_ACCOUNT_NAME.blob.core.windows.net")
                .withCopyToContainer(
                    MountableFile.forHostPath(nginxConf.path),
                    "/etc/nginx/nginx.conf"
                )
                .withLogConsumer { e -> logger.debug { e.utf8String } }

        nginx.start()
    }

    private fun prepareDatabaseForBulkInsert() {
        val connectionUrl = createDatabaseConnectionUrl()
        DriverManager.getConnection(connectionUrl).use { connection ->
            connection.createStatement().use { statement ->
                statement.execute(
                    """
                            IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '$DATABASE_NAME')
                            BEGIN
                                CREATE DATABASE [$DATABASE_NAME];
                            END
                        """.trimIndent()
                )
                statement.execute(
                    """
                            USE [$DATABASE_NAME];
                            IF NOT EXISTS(SELECT * FROM sys.external_data_sources WHERE name = '$DATA_SOURCE_NAME')
                            BEGIN
                                CREATE MASTER KEY ENCRYPTION BY PASSWORD = '$MASTER_ENCRYPTION_PASSWORD';
                                CREATE DATABASE SCOPED CREDENTIAL $BLOB_STORAGE_CREDENTIAL WITH IDENTITY = 'SHARED ACCESS SIGNATURE', SECRET = '${getSharedAccessSignature()}';
                                CREATE EXTERNAL DATA SOURCE $DATA_SOURCE_NAME WITH ( TYPE = BLOB_STORAGE, LOCATION = '${createBlobContainerUrl()}', CREDENTIAL = $BLOB_STORAGE_CREDENTIAL);
                            END
                        """.trimIndent(),
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

    private fun createBlobContainerUrl(): String {
        return "http://$WELL_KNOWN_ACCOUNT_NAME.blob.core.windows.net/${getBlobContainer()}"
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
