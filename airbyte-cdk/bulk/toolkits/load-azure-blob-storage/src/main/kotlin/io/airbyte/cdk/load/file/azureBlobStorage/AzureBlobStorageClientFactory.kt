/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.identity.ClientSecretCredentialBuilder
import com.azure.storage.blob.BlobServiceClientBuilder
import com.azure.storage.common.StorageSharedKeyCredential
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfigurationProvider
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Factory
class AzureBlobStorageClientFactory(
    private val azureBlobStorageClientConfigurationProvider:
        AzureBlobStorageClientConfigurationProvider,
) {

    @Singleton
    @Secondary
    fun make(): AzureBlobClient {
        val endpoint =
            "https://${azureBlobStorageClientConfigurationProvider.azureBlobStorageClientConfiguration.accountName}.blob.core.windows.net"

        val config = azureBlobStorageClientConfigurationProvider.azureBlobStorageClientConfiguration

        val clientBuilder = BlobServiceClientBuilder().endpoint(endpoint)
        when {
            // EntraId config is available
            !config.tenantId.isNullOrBlank() &&
                !config.clientId.isNullOrBlank() &&
                !config.clientSecret.isNullOrBlank() -> {
                val credential =
                    ClientSecretCredentialBuilder()
                        .tenantId(config.tenantId)
                        .clientId(config.clientId)
                        .clientSecret(config.clientSecret)
                        .build()
                clientBuilder.credential(credential)
            }

            // Shared Access Signature config is available
            !config.sharedAccessSignature.isNullOrBlank() ->
                clientBuilder.sasToken(config.sharedAccessSignature)

            // Otherwise fallback to using an account key
            !config.accountKey.isNullOrBlank() -> {
                val credential = StorageSharedKeyCredential(config.accountName, config.accountKey)
                clientBuilder.credential(credential)
            }
            else -> {
                throw IllegalStateException(
                    "No valid authentication method provided for Azure Blob Storage"
                )
            }
        }

        val azureServiceClient = clientBuilder.buildClient()
        return AzureBlobClient(
            azureServiceClient,
            azureBlobStorageClientConfigurationProvider.azureBlobStorageClientConfiguration,
        )
    }
}
