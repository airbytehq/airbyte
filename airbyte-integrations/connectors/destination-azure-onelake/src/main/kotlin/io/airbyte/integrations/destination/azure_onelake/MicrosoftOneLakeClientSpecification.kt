/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_onelake

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientSpecification
import io.airbyte.cdk.load.command.object_storage.JsonFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.micronaut.context.annotation.Primary
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

/**
 * Microsoft OneLake Destination Specification.
 *
 * OneLake exposes an ABFS-compatible endpoint:
 *   abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<item>.<itemtype>/<path>/
 *
 * Authentication: either Azure Service Principal (Tenant ID + Client ID + Client Secret)
 * or Managed Identity (use_managed_identity=true). Account-key auth is NOT supported by OneLake.
 */
@Singleton
@Primary
@JsonSchemaTitle("Microsoft OneLake Destination Spec")
@JsonSchemaInject()
class MicrosoftOneLakeSpecification :
    ConfigurationSpecification(),
    AzureBlobStorageClientSpecification,
    ObjectStorageFormatSpecificationProvider {

    // Same structure as Azure Blob Storage spec so the Airbyte UI form works (no hidden/auth overrides).
    @get:JsonSchemaTitle("Azure Storage Endpoint Domain Name")
    @get:JsonPropertyDescription(
        "OneLake uses a fixed endpoint. Leave default for Microsoft Fabric OneLake."
    )
    @get:JsonProperty("azure_blob_storage_endpoint_domain_name")
    val azureBlobStorageEndpointDomainName: String? = "onelake.dfs.fabric.microsoft.com"

    @get:JsonSchemaTitle("Fabric Workspace Name or GUID")
    @get:JsonPropertyDescription(
        "The name or GUID of your Microsoft Fabric workspace. Use GUID if the name has spaces."
    )
    @get:JsonProperty("azure_blob_storage_account_name")
    @get:JsonSchemaInject(json = """{"examples":["mystorageaccount"]}""")
    override val azureBlobStorageAccountName: String = ""

    @get:JsonSchemaTitle("Lakehouse Item Path")
    @get:JsonPropertyDescription(
        "The Lakehouse (or Fabric item) that will receive the data. E.g. 'MyLakehouse.Lakehouse' or 'lakehouse_raw'."
    )
    @get:JsonProperty("azure_blob_storage_container_name")
    @get:JsonSchemaInject(json = """{"examples":["mycontainer"]}""")
    override val azureBlobStorageContainerName: String = ""

    override val azureBlobStorageSharedAccessSignature: String? = null

    override val azureBlobStorageAccountKey: String? = null

    override val azureTenantId: String? = null

    override val azureClientId: String? = null

    override val azureClientSecret: String? = null

    @get:JsonSchemaTitle("Use Managed Identity")
    @get:JsonPropertyDescription(
        "Use the Azure Managed Identity of the host (e.g. Airbyte runner) instead of Service Principal. " +
            "Requires the identity to have Storage Blob Data Contributor (or similar) on the Fabric workspace."
    )
    @get:JsonProperty("use_managed_identity")
    @JsonSchemaInject(json = """{"default": false}""")
    override val useManagedIdentity: Boolean = false

    @get:JsonSchemaTitle("Managed Identity Client ID (optional)")
    @get:JsonPropertyDescription(
        "For user-assigned Managed Identity, set this to the identity's client ID. Leave empty for system-assigned."
    )
    @get:JsonProperty("managed_identity_client_id")
    override val managedIdentityClientId: String? = null

    @get:JsonSchemaTitle("Target Object Size (MB)")
    @get:JsonPropertyDescription(
        "The amount of megabytes after which the connector should spill to a new blob. Enter 0 if not applicable."
    )
    @get:JsonProperty("azure_blob_storage_spill_size")
    @JsonSchemaInject(json = """{"default": 500}""")
    val azureBlobStorageSpillSize: Int? = 500

    @get:JsonSchemaTitle("Output Path Format")
    @get:JsonPropertyDescription(
        "Format of the output directory inside the Lakehouse Files section. Variables: \${NAMESPACE}, \${STREAM_NAME}, etc. Leave empty for default."
    )
    @get:JsonProperty("destination_path_format")
    @JsonSchemaInject(
        json = "{\"examples\":[\"${'$'}{NAMESPACE}/${'$'}{STREAM_NAME}/\"],\"default\":\"\"}"
    )
    val pathFormat: String? = ""

    @get:JsonSchemaTitle("File Name Pattern")
    @get:JsonPropertyDescription(
        "Pattern for output file names. Variables: {date}, {timestamp}, {part_number}, {format_extension}. Leave empty for default."
    )
    @get:JsonProperty("file_name_pattern")
    @JsonSchemaInject(json = """{"examples":["{date}_{timestamp}_{part_number}{format_extension}"],"default":""}""")
    val fileNamePattern: String? = ""

    // OneLake-only: subpath under Files/ (default: "data"). Hidden; config factory defaults to "data" if missing.
    @get:JsonProperty("one_lake_files_sub_path")
    @get:JsonSchemaInject(json = """{"airbyte_hidden": true, "default": "data"}""")
    val oneLakeFilesSubPath: String? = "data"

    override val format: ObjectStorageFormatSpecification = JsonFormatSpecification()
}

@Singleton
@Primary
class MicrosoftOneLakeSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
        )
    override val supportsIncremental = true
}

