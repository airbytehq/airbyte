/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.storage.blob.BlobServiceClientBuilder
import io.airbyte.cdk.load.command.azureBlobStorage.BaseAzureBlobStorageConfigurationProvider
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Factory
class AzureBlobStorageClientFactory(
    private val baseAzureBlobStorageConfigurationProvider:
        BaseAzureBlobStorageConfigurationProvider,
) {

    @Singleton
    @Secondary
    fun make(): AzureBlobClient {
        val endpoint =
            "https://${baseAzureBlobStorageConfigurationProvider.baseAzureBlobStorageConfiguration.accountName}.blob.core.windows.net"

        val azureServiceClient =
            BlobServiceClientBuilder()
                .endpoint(endpoint)
                .sasToken(
                    baseAzureBlobStorageConfigurationProvider.baseAzureBlobStorageConfiguration
                        .sharedAccessSignature
                )
                .buildClient()

        return AzureBlobClient(
            azureServiceClient,
            baseAzureBlobStorageConfigurationProvider.baseAzureBlobStorageConfiguration
        )
    }
}
