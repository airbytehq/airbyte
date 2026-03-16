/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

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
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Azure Blob Storage Destination Spec")
@JsonSchemaInject()
class AzureBlobStorageSpecification :
    ConfigurationSpecification(),
    AzureBlobStorageClientSpecification,
    ObjectStorageFormatSpecificationProvider {

    @get:JsonSchemaTitle("Azure Blob Storage Endpoint Domain Name")
    @get:JsonPropertyDescription(
        "This is Azure Blob Storage endpoint domain name. Leave default value (or leave it empty if run container from command line) to use Microsoft native from example."
    )
    @get:JsonProperty("azure_blob_storage_endpoint_domain_name")
    val azureBlobStorageEndpointDomainName: String? = "blob.core.windows.net"

    override val azureBlobStorageAccountName: String = ""

    override val azureBlobStorageContainerName: String = ""

    override val azureBlobStorageSharedAccessSignature: String? = null

    override val azureBlobStorageAccountKey: String? = null

    override val azureTenantId: String? = null

    override val azureClientId: String? = null

    override val azureClientSecret: String? = null

    @get:JsonSchemaTitle("Azure Blob Storage Target Blob Size (MB)")
    @get:JsonPropertyDescription(
        "The amount of megabytes after which the connector should spill the records in a new blob object. Make sure to configure size greater than individual records. Enter 0 if not applicable."
    )
    @get:JsonProperty("azure_blob_storage_spill_size")
    @JsonSchemaInject(json = """{"default": 500}""")
    val azureBlobStorageSpillSize: Int? = 500

    /**
     * Configurable path format using variable placeholders.
     * Supported variables: ${NAMESPACE}, ${STREAM_NAME}, ${YEAR}, ${MONTH}, ${DAY},
     *   ${HOUR}, ${MINUTE}, ${SECOND}, ${MILLISECOND}, ${EPOCH}, ${UUID}
     */
    @get:JsonSchemaTitle("Output Path Format")
    @get:JsonPropertyDescription(
        "Format of the output directory/path inside the container. " +
            "You can use the following variables: " +
            "\${NAMESPACE}, \${STREAM_NAME}, \${YEAR}, \${MONTH}, \${DAY}, " +
            "\${HOUR}, \${MINUTE}, \${SECOND}, \${MILLISECOND}, \${EPOCH}, \${UUID}. " +
            "Leave empty to use the default: \${NAMESPACE}/\${STREAM_NAME}/"
    )
    @get:JsonProperty("destination_path_format")
    @JsonSchemaInject(
        json = "{\"examples\":[\"${'$'}{NAMESPACE}/${'$'}{STREAM_NAME}/\",\"${'$'}{NAMESPACE}/${'$'}{STREAM_NAME}/${'$'}{YEAR}/${'$'}{MONTH}/${'$'}{DAY}/\",\"${'$'}{STREAM_NAME}/${'$'}{YEAR}_${'$'}{MONTH}_${'$'}{DAY}/\"]}"
    )
    val pathFormat: String? = null

    /**
     * Configurable file name pattern using variable placeholders.
     * Supported variables: {date}, {date:yyyy_MM}, {timestamp}, {part_number},
     *   {sync_id}, {format_extension}
     */
    @get:JsonSchemaTitle("File Name Pattern")
    @get:JsonPropertyDescription(
        "Pattern for the output file names. " +
            "You can use the following variables: " +
            "{date}, {date:yyyy_MM}, {timestamp}, {part_number}, {sync_id}, {format_extension}. " +
            "Leave empty to use the default: {date}_{timestamp}_{part_number}{format_extension}"
    )
    @get:JsonProperty("file_name_pattern")
    @JsonSchemaInject(
        json = """{"examples":["{date}_{timestamp}_{part_number}{format_extension}","{sync_id}_{date}_{part_number}{format_extension}"]}"""
    )
    val fileNamePattern: String? = null

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
