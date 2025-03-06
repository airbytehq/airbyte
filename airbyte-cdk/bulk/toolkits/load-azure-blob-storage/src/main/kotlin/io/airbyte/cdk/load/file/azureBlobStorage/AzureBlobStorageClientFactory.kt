/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.storage.blob.BlobServiceClientBuilder
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageConfigurationProvider
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Factory
class AzureBlobStorageClientFactory(
    private val azureBlobStorageConfigurationProvider: AzureBlobStorageConfigurationProvider,
) {

    @Singleton
    @Secondary
    fun make(): AzureBlobClient {
        val endpoint =
            "https://${azureBlobStorageConfigurationProvider.azureBlobStorageConfiguration.accountName}.blob.core.windows.net"

        val azureServiceClient =
            BlobServiceClientBuilder()
                .endpoint(endpoint)
                .sasToken(
                    azureBlobStorageConfigurationProvider.azureBlobStorageConfiguration
                        .sharedAccessSignature
                )
                .buildClient()

        return AzureBlobClient(
            azureServiceClient,
            azureBlobStorageConfigurationProvider.azureBlobStorageConfiguration
        )
    }
}
