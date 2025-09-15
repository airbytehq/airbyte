/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

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

        val azureServiceClient =
            if (
                azureBlobStorageClientConfigurationProvider.azureBlobStorageClientConfiguration
                    .sharedAccessSignature
                    .isNullOrBlank()
            ) {
                val credential =
                    StorageSharedKeyCredential(
                        azureBlobStorageClientConfigurationProvider
                            .azureBlobStorageClientConfiguration
                            .accountName,
                        azureBlobStorageClientConfigurationProvider
                            .azureBlobStorageClientConfiguration
                            .accountKey,
                    )

                BlobServiceClientBuilder().endpoint(endpoint).credential(credential).buildClient()
            } else {
                BlobServiceClientBuilder()
                    .endpoint(endpoint)
                    .sasToken(
                        azureBlobStorageClientConfigurationProvider
                            .azureBlobStorageClientConfiguration
                            .sharedAccessSignature,
                    )
                    .buildClient()
            }

        return AzureBlobClient(
            azureServiceClient,
            azureBlobStorageClientConfigurationProvider.azureBlobStorageClientConfiguration,
        )
    }
}
