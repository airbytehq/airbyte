/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.azureBlobStorage.BaseAzureBlobStorageSpecification
import io.airbyte.cdk.load.command.object_storage.JsonFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

class AzureBlobStorageSpecification :
    ConfigurationSpecification(),
    BaseAzureBlobStorageSpecification,
    ObjectStorageFormatSpecificationProvider {
    override val azureBlobStorageAccountName: String
        get() = TODO("Not yet implemented")

    override val azureBlobStorageContainerName: String
        get() = TODO("Not yet implemented")

    override val azureBlobStorageSharedAccessSignature: String
        get() = TODO("Not yet implemented")

    override val format: ObjectStorageFormatSpecification = JsonFormatSpecification()
}

@Singleton
class AzureBlobStorageSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
        )
    override val supportsIncremental = true
}
