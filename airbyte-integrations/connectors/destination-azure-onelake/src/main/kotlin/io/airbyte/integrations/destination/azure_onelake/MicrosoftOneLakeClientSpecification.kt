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
    @get:JsonSchemaInject(
        json = """{"group":"onelake","order":0}"""
    )
    val azureBlobStorageEndpointDomainName: String? = "onelake.dfs.fabric.microsoft.com"

    @get:JsonSchemaTitle("Fabric Workspace Name or GUID")
    @get:JsonPropertyDescription(
        "The name or GUID of your Microsoft Fabric workspace. Use GUID if the name has spaces."
    )
    @get:JsonProperty("azure_blob_storage_account_name")
    @get:JsonSchemaInject(
        json = """{"group":"onelake","examples":["mystorageaccount"],"order":1}"""
    )
    override val azureBlobStorageAccountName: String = ""

    @get:JsonSchemaTitle("Lakehouse Item Path")
    @get:JsonPropertyDescription(
        "The Lakehouse (or Fabric item) that will receive the data. E.g. 'MyLakehouse.Lakehouse' or 'lakehouse_raw'."
    )
    @get:JsonProperty("azure_blob_storage_container_name")
    @get:JsonSchemaInject(
        json = """{"group":"onelake","examples":["mycontainer"],"order":2}"""
    )
    override val azureBlobStorageContainerName: String = ""

    // Not supported for OneLake; kept for schema compatibility. Placed at end of form via order.
    @get:JsonSchemaTitle("Shared Access Signature")
    @get:JsonPropertyDescription("Not used for OneLake. Leave empty.")
    @get:JsonProperty("shared_access_signature")
    @get:JsonSchemaInject(
        json =
            """{"group":"onelake","order":12,"airbyte_hidden":true,"examples":["sv=2021-08-06&st=2025-04-11T00%3A00%3A00Z&se=2025-04-12T00%3A00%3A00Z&sr=b&sp=rw&sig=abcdefghijklmnopqrstuvwxyz1234567890%2Fabcdefg%3D"],"airbyte_secret":true}"""
    )
    override val azureBlobStorageSharedAccessSignature: String? = null

    @get:JsonSchemaTitle("Azure Blob Storage Account Key")
    @get:JsonPropertyDescription("Not used for OneLake. Leave empty.")
    @get:JsonProperty("azure_blob_storage_account_key")
    @get:JsonSchemaInject(
        json =
            """{"group":"onelake","order":13,"airbyte_hidden":true,"examples":["Z8ZkZpteggFx394vm+PJHnGTvdRncaYS+JhLKdj789YNmD+iyGTnG+PV+POiuYNhBg/ACS+LKjd%4FG3FHGN12Nd=="],"airbyte_secret":true}"""
    )
    override val azureBlobStorageAccountKey: String? = null

    // IMPORTANT:
    // Do NOT override these as plain nullable properties without schema annotations.
    // Airbyte relies on `airbyte_secret` to know when to preserve existing values on edit.
    // If we drop the secret annotation, the UI will send masked placeholders (e.g. "********")
    // and the platform will persist that literal value, breaking auth until the user re-enters creds.

    @get:JsonSchemaTitle("Azure Tenant ID")
    @get:JsonPropertyDescription(
        "The Azure Active Directory (Entra ID) tenant ID. Required for Entra ID authentication."
    )
    @get:JsonProperty("azure_tenant_id")
    @get:JsonSchemaInject(
        json = """{"group":"onelake","examples":["12345678-1234-1234-1234-123456789012"],"airbyte_secret":false,"order":6}"""
    )
    override val azureTenantId: String? = ""

    @get:JsonSchemaTitle("Azure Client ID")
    @get:JsonPropertyDescription(
        "The Azure Active Directory (Entra ID) client ID. Required for Entra ID authentication."
    )
    @get:JsonProperty("azure_client_id")
    @get:JsonSchemaInject(
        json = """{"group":"onelake","examples":["87654321-4321-4321-4321-210987654321"],"airbyte_secret":false,"order":7}"""
    )
    override val azureClientId: String? = ""

    @get:JsonSchemaTitle("Use Managed Identity")
    @get:JsonPropertyDescription(
        "Use the Azure Managed Identity of the host (e.g. Airbyte runner) instead of Service Principal. " +
            "Requires the identity to have Storage Blob Data Contributor (or similar) on the Fabric workspace."
    )
    @get:JsonProperty("use_managed_identity")
    @JsonSchemaInject(json = """{"group":"onelake","default":false,"order":4}""")
    override val useManagedIdentity: Boolean = false

    @get:JsonSchemaTitle("Managed Identity Client ID (optional)")
    @get:JsonPropertyDescription(
        "For user-assigned Managed Identity, set this to the identity's client ID. Leave empty for system-assigned."
    )
    @get:JsonProperty("managed_identity_client_id")
    @get:JsonSchemaInject(json = """{"group":"onelake","order":5}""")
    override val managedIdentityClientId: String? = null

    @get:JsonSchemaTitle("Target Object Size (MB)")
    @get:JsonPropertyDescription(
        "The amount of megabytes after which the connector should spill to a new blob. Enter 0 if not applicable."
    )
    @get:JsonProperty("azure_blob_storage_spill_size")
    @JsonSchemaInject(json = """{"group":"onelake","default":500,"order":9}""")
    val azureBlobStorageSpillSize: Int? = 500

    @get:JsonSchemaTitle("Output Path Format")
    @get:JsonPropertyDescription(
        "Format of the output directory inside the Lakehouse Files section. Variables: \${NAMESPACE}, \${STREAM_NAME}, etc. Leave empty for default."
    )
    @get:JsonProperty("destination_path_format")
    @JsonSchemaInject(
        json = "{\"group\":\"onelake\",\"examples\":[\"${'$'}{NAMESPACE}/${'$'}{STREAM_NAME}/\"],\"default\":\"\",\"order\":10}"
    )
    val pathFormat: String? = ""

    @get:JsonSchemaTitle("File Name Pattern")
    @get:JsonPropertyDescription(
        "Pattern for output file names. Variables: {date}, {timestamp}, {part_number}, {format_extension}. Leave empty for default."
    )
    @get:JsonProperty("file_name_pattern")
    @JsonSchemaInject(
        json = """{"group":"onelake","examples":["{date}_{timestamp}_{part_number}{format_extension}"],"default":"","order":11}"""
    )
    val fileNamePattern: String? = ""

    @get:JsonSchemaTitle("Azure Client Secret")
    @get:JsonPropertyDescription(
        "The Azure Active Directory (Entra ID) client secret. Required when Use Managed Identity is off. " +
            "Enter after Tenant ID and Client ID."
    )
    @get:JsonProperty("azure_client_secret")
    @get:JsonSchemaInject(
        json = """{"group":"onelake","examples":["your-client-secret"],"airbyte_secret":true,"order":8}"""
    )
    override val azureClientSecret: String? = ""

    // OneLake-only: subpath under Files/. Hidden; config factory applies "data" only when
    // destination_path_format is left empty, otherwise it leaves this blank so the user's
    // custom path is respected.
    @get:JsonProperty("one_lake_files_sub_path")
    @get:JsonSchemaInject(
        json = """{"group":"onelake","airbyte_hidden":true,"default":"","order":99}"""
    )
    val oneLakeFilesSubPath: String? = ""

    @get:JsonProperty("format")
    @get:JsonSchemaInject(json = """{"group":"onelake","order":3}""")
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
    override val groups =
        listOf(
            DestinationSpecificationExtension.Group("onelake", "Microsoft OneLake"),
        )
}

