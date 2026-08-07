/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.identity.AzureAuthorityHosts
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

    private fun resolveAuthorityHost(endpointDomainName: String): String {
        return when {
            endpointDomainName.endsWith("core.usgovcloudapi.net", ignoreCase = true) ->
                AzureAuthorityHosts.AZURE_GOVERNMENT
            endpointDomainName.endsWith("core.chinacloudapi.cn", ignoreCase = true) ->
                AzureAuthorityHosts.AZURE_CHINA
            else -> AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
        }
    }

    @Singleton
    @Secondary
    fun make(): AzureBlobClient {
        val config = azureBlobStorageClientConfigurationProvider.azureBlobStorageClientConfiguration
        val endpointDomainName =
            config.endpointDomainName?.takeIf { it.isNotBlank() } ?: "blob.core.windows.net"
        val endpoint = "https://${config.accountName}.$endpointDomainName"

        val clientBuilder = BlobServiceClientBuilder().endpoint(endpoint)
        when {
            // EntraId config is available
            !config.tenantId.isNullOrBlank() &&
                !config.clientId.isNullOrBlank() &&
                !config.clientSecret.isNullOrBlank() -> {
                val credential =
                    ClientSecretCredentialBuilder()
                        .authorityHost(resolveAuthorityHost(endpointDomainName))
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
