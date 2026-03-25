/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.identity.ClientSecretCredentialBuilder
import com.azure.identity.DefaultAzureCredentialBuilder
import com.azure.identity.ManagedIdentityCredentialBuilder
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
        val config = azureBlobStorageClientConfigurationProvider.azureBlobStorageClientConfiguration

        val endpoint =
            config.endpointUrl
                ?: "https://${config.accountName}.blob.core.windows.net"

        val clientBuilder = BlobServiceClientBuilder().endpoint(endpoint)
        when {
            // Managed Identity (system-assigned or user-assigned)
            config.useManagedIdentity -> {
                val credential =
                    if (!config.managedIdentityClientId.isNullOrBlank()) {
                        ManagedIdentityCredentialBuilder()
                            .clientId(config.managedIdentityClientId)
                            .build()
                    } else {
                        DefaultAzureCredentialBuilder().build()
                    }
                clientBuilder.credential(credential)
            }

            // EntraId (Service Principal) config is available
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
