/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
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

    @get:JsonSchemaTitle("Azure Blob Storage target blob size (Megabytes)")
    @get:JsonPropertyDescription(
        "The amount of megabytes after which the connector should spill the records in a new blob object. Make sure to configure size greater than individual records. Enter 0 if not applicable."
    )
    @get:JsonProperty("azure_blob_storage_spill_size")
    @JsonSchemaInject(json = """{"default": 500}""")
    val azureBlobStorageSpillSize: Int? = 500

    override val format: ObjectStorageFormatSpecification = JsonFormatSpecification()

    @get:JsonProperty("num_sockets") val numSockets: Int? = null

    @get:JsonProperty("num_part_loaders") val numPartLoaders: Int? = null

    @get:JsonProperty("input_serialization_format")
    val inputSerializationFormat: DestinationConfiguration.InputSerializationFormat? = null

    @get:JsonProperty("max_memory_ratio_reserved_for_parts")
    val maxMemoryRatioReservedForParts: Double? = null

    @get:JsonProperty("part_size_mb") val partSizeMb: Int? = null

    @get:JsonProperty("input_buffer_byte_size_per_socket")
    val inputBufferByteSizePerSocket: Long? = null

    @get:JsonProperty("socket_prefix") val socketPrefix: String? = null

    @get:JsonProperty("socket_wait_timeout_seconds") val socketWaitTimeoutSeconds: Int? = null

    @get:JsonProperty("dev_null_after_deserialization")
    val devNullAfterDeserialization: Boolean? = null

    @get:JsonProperty("skip_upload") val skipUpload: Boolean? = null

    @get:JsonProperty("use_garbage_part") val useGarbagePart: Boolean? = null

    @get:JsonProperty("num_part_formatters") val numPartFormatters: Int? = null

    @get:JsonProperty("skip_json_on_proto") val skipJsonOnProto: Boolean? = null

    @get:JsonProperty("disable_uuid") val disableUUID: Boolean? = null

    @get:JsonProperty("disable_mapper") val disableMapper: Boolean? = null

    @get:JsonProperty("use_coded_input_stream") val useCodedInputStream: Boolean? = null

    @get:JsonProperty("use_snappy") val useSnappy: Boolean? = null
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
