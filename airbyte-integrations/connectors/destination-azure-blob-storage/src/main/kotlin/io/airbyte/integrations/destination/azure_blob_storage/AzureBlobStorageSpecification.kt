/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.azureBlobStorage.BaseAzureBlobStorageSpecification
import io.airbyte.cdk.load.command.object_storage.JsonFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Azure Blob Storage Destination Spec")
@JsonSchemaInject()
class AzureBlobStorageSpecification :
    ConfigurationSpecification(),
    BaseAzureBlobStorageSpecification,
    ObjectStorageFormatSpecificationProvider {

    @get:JsonSchemaTitle("Azure Blob Storage Endpoint Domain Name")
    @get:JsonPropertyDescription(
        "This is Azure Blob Storage endpoint domain name. Leave default value (or leave it empty if run container from command line) to use Microsoft native from example."
    )
    @get:JsonProperty("azure_blob_storage_endpoint_domain_name")
    val azureBlobStorageEndpointDomainName: String? = "blob.core.windows.net"

    override val azureBlobStorageAccountName: String = ""

    override val azureBlobStorageContainerName: String = ""

    override val azureBlobStorageSharedAccessSignature: String = ""

    @get:JsonSchemaTitle("Azure Blob Storage file spill size (Megabytes)")
    @get:JsonPropertyDescription(
        "The amount of megabytes after which the connector should spill the records in a new blob object. Make sure to configure size greater than individual records. Enter 0 if not applicable."
    )
    @get:JsonProperty("azure_blob_storage_spill_size")
    val azureBlobStorageSpillSize: Int? = 500

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
