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
interface AzureBlobStorageClientSpecification {
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
        "A shared access signature (SAS) provides secure delegated access to resources in your storage account. Read more <a href=\"https://learn.microsoft.com/en-gb/azure/storage/common/storage-sas-overview?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json&bc=%2Fazure%2Fstorage%2Fblobs%2Fbreadcrumb%2Ftoc.json\">here</a>. If you set this value, you must not set the account key or Entra ID authentication."
    )
    @get:JsonProperty("shared_access_signature")
    @get:JsonSchemaInject(
        json =
            """{"examples":["sv=2021-08-06&st=2025-04-11T00%3A00%3A00Z&se=2025-04-12T00%3A00%3A00Z&sr=b&sp=rw&sig=abcdefghijklmnopqrstuvwxyz1234567890%2Fabcdefg%3D"],"airbyte_secret": true,"always_show": true}"""
    )
    val azureBlobStorageSharedAccessSignature: String?

    @get:JsonSchemaTitle("Azure Blob Storage account key")
    @get:JsonPropertyDescription(
        "The Azure blob storage account key. If you set this value, you must not set the Shared Access Signature or Entra ID authentication."
    )
    @get:JsonProperty("azure_blob_storage_account_key")
    @get:JsonSchemaInject(
        json =
            """{"examples":["Z8ZkZpteggFx394vm+PJHnGTvdRncaYS+JhLKdj789YNmD+iyGTnG+PV+POiuYNhBg/ACS+LKjd%4FG3FHGN12Nd=="],"airbyte_secret": true,"always_show": true}"""
    )
    val azureBlobStorageAccountKey: String?

    @get:JsonSchemaTitle("Azure Tenant ID")
    @get:JsonPropertyDescription(
        "The Azure Active Directory (Entra ID) tenant ID. Required for Entra ID authentication."
    )
    @get:JsonProperty("azure_tenant_id")
    @get:JsonSchemaInject(
        json = """{"examples":["12345678-1234-1234-1234-123456789012"],"airbyte_secret": false}"""
    )
    val azureTenantId: String?

    @get:JsonSchemaTitle("Azure Client ID")
    @get:JsonPropertyDescription(
        "The Azure Active Directory (Entra ID) client ID. Required for Entra ID authentication."
    )
    @get:JsonProperty("azure_client_id")
    @get:JsonSchemaInject(
        json = """{"examples":["87654321-4321-4321-4321-210987654321"],"airbyte_secret": false}"""
    )
    val azureClientId: String?

    @get:JsonSchemaTitle("Azure Client Secret")
    @get:JsonPropertyDescription(
        "The Azure Active Directory (Entra ID) client secret. Required for Entra ID authentication."
    )
    @get:JsonProperty("azure_client_secret")
    @get:JsonSchemaInject(
        json = """{"examples":["your-client-secret"],"airbyte_secret": true,"always_show": true}"""
    )
    val azureClientSecret: String?

    fun toAzureBlobStorageClientConfiguration(): AzureBlobStorageClientConfiguration {
        return AzureBlobStorageClientConfiguration(
            azureBlobStorageAccountName,
            azureBlobStorageContainerName,
            azureBlobStorageSharedAccessSignature,
            azureBlobStorageAccountKey,
            azureTenantId,
            azureClientId,
            azureClientSecret
        )
    }
}

data class AzureBlobStorageClientConfiguration(
    val accountName: String,
    val containerName: String,
    val sharedAccessSignature: String?,
    val accountKey: String?,
    val tenantId: String?,
    val clientId: String?,
    val clientSecret: String?,

    // The following is only used by the azure blob storage destination
    var endpointDomainName: String? = null,
    var spillSize: Int? = null,
) {
    init {
        val hasAccountKey = !accountKey.isNullOrBlank()
        val hasSas = !sharedAccessSignature.isNullOrBlank()
        val hasEntraId =
            !tenantId.isNullOrBlank() && !clientId.isNullOrBlank() && !clientSecret.isNullOrBlank()

        val authMethods = listOf(hasAccountKey, hasSas, hasEntraId).count { it }
        check(authMethods == 1) {
            "AzureBlobStorageClientConfiguration must have exactly one of: account key, SAS token, or Entra ID authentication (tenant ID, client ID, and client secret)"
        }
    }
}

interface AzureBlobStorageClientConfigurationProvider {
    val azureBlobStorageClientConfiguration: AzureBlobStorageClientConfiguration
}
