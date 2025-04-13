/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfiguration
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfigurationProvider
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobClient
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobStorageClientFactory

object AzureBlobStorageClientCreator {

    /**
     * Creates an [AzureBlobClient] based on the [BulkLoadConfiguration]. This method is only called
     * if the load configuration is Azure Blob.
     */
    fun createAzureBlobClient(bulkLoadConfiguration: BulkLoadConfiguration): AzureBlobClient {
        val configProvider =
            object : AzureBlobStorageClientConfigurationProvider {
                override val azureBlobStorageClientConfiguration =
                    AzureBlobStorageClientConfiguration(
                        accountName = bulkLoadConfiguration.accountName,
                        containerName = bulkLoadConfiguration.containerName,
                        sharedAccessSignature = bulkLoadConfiguration.sharedAccessSignature,
                        accountKey = bulkLoadConfiguration.accountKey,
                    )
            }
        return AzureBlobStorageClientFactory(configProvider).make()
    }
}
