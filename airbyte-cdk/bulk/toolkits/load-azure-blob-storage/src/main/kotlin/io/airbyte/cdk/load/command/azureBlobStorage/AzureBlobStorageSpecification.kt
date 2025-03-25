/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.azureBlobStorage

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/**
 * Mix-in to provide Azure Blob Storage configuration fields as properties.
 *
 * See [io.airbyte.cdk.load.command.DestinationConfiguration] for more details on how to use this
 * interface.
 */
interface AzureBlobStorageSpecification {
    @get:JsonSchemaTitle("Azure Blob Storage Account Name")
    @get:JsonPropertyDescription(
        "The name of the Azure Blob Storage Account. Read more <a href=\"https://learn.microsoft.com/en-gb/azure/storage/blobs/storage-blobs-introduction#storage-accounts\">here</a>."
    )
    @get:JsonProperty("azure_blob_storage_account_name")
    @get:JsonSchemaInject(json = """{"examples":["mystorageaccount"]}""")
    val azureBlobStorageAccountName: String

    @get:JsonSchemaTitle("Azure Blob Storage Container Name")
    @get:JsonPropertyDescription(
        "The name of the Azure Blob Storage Container. Read more <a href=\"https://learn.microsoft.com/en-gb/azure/storage/blobs/storage-blobs-introduction#containers\">here</a>."
    )
    @get:JsonProperty("azure_blob_storage_container_name")
    @get:JsonSchemaInject(json = """{"examples":["mycontainer"]}""")
    val azureBlobStorageContainerName: String

    @get:JsonSchemaTitle("Shared Access Signature")
    @get:JsonPropertyDescription(
        "A shared access signature (SAS) provides secure delegated access to resources in your storage account.. Read more <a href=\"https://learn.microsoft.com/en-gb/azure/storage/common/storage-sas-overview?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json&bc=%2Fazure%2Fstorage%2Fblobs%2Fbreadcrumb%2Ftoc.json\">here</a>"
    )
    @get:JsonProperty("shared_access_signature")
    @get:JsonSchemaInject(
        json =
            """{"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"],"airbyte_secret": true,"always_show": true}"""
    )
    val azureBlobStorageSharedAccessSignature: String

    fun toAzureBlobStorageConfiguration(): AzureBlobStorageConfiguration {
        return AzureBlobStorageConfiguration(
            azureBlobStorageAccountName,
            azureBlobStorageContainerName,
            azureBlobStorageSharedAccessSignature
        )
    }
}

data class AzureBlobStorageConfiguration(
    val accountName: String,
    val containerName: String,
    val sharedAccessSignature: String
)

interface AzureBlobStorageConfigurationProvider {
    val azureBlobStorageConfiguration: AzureBlobStorageConfiguration
}
