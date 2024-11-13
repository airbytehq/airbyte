/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.StreamProcessor
import java.io.ByteArrayOutputStream
import java.io.OutputStream

/**
 * Mix-in to provide file format configuration.
 *
 * The specification is intended to be applied to file formats that are compatible with file-level
 * compression (csv, jsonl) and does not need to be added to the destination spec directly. The
 * [ObjectStorageCompressionConfigurationProvider] can be added to the top-level
 * [io.airbyte.cdk.load.command.DestinationConfiguration] and initialized directly with
 * [ObjectStorageFormatSpecificationProvider.toObjectStorageFormatConfiguration]. (See the comments
 * on [io.airbyte.cdk.load.command.DestinationConfiguration] for more details.)
 */
interface ObjectStorageCompressionSpecificationProvider {
    @get:JsonSchemaTitle("Compression")
    @get:JsonPropertyDescription(
        "Whether the output files should be compressed. If compression is selected, the output filename will have an extra extension (GZIP: \".jsonl.gz\").",
    )
    @get:JsonProperty("compression")
    val compression: ObjectStorageCompressionSpecification

    fun toCompressionConfiguration(): ObjectStorageCompressionConfiguration<*> {
        return when (compression) {
            is NoCompressionSpecification -> ObjectStorageCompressionConfiguration(NoopProcessor)
            is GZIPCompressionSpecification -> ObjectStorageCompressionConfiguration(GZIPProcessor)
        }
    }

    companion object {
        fun getNoCompressionConfiguration():
            ObjectStorageCompressionConfiguration<ByteArrayOutputStream> {
            return ObjectStorageCompressionConfiguration(NoopProcessor)
        }
    }
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "compression_type",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = NoCompressionSpecification::class, name = "No Compression"),
    JsonSubTypes.Type(value = GZIPCompressionSpecification::class, name = "GZIP"),
)
sealed class ObjectStorageCompressionSpecification(
    @JsonProperty("compression_type") open val compressionType: Type
) {
    enum class Type(@get:JsonValue val typeName: String) {
        NoCompression("No Compression"),
        GZIP("GZIP"),
    }
}

@JsonSchemaTitle("No Compression")
class NoCompressionSpecification(
    @JsonProperty("compression_type") override val compressionType: Type = Type.NoCompression
) : ObjectStorageCompressionSpecification(compressionType)

@JsonSchemaTitle("GZIP")
class GZIPCompressionSpecification(
    @JsonProperty("compression_type") override val compressionType: Type = Type.GZIP
) : ObjectStorageCompressionSpecification(compressionType)

data class ObjectStorageCompressionConfiguration<T : OutputStream>(
    val compressor: StreamProcessor<T>
)

interface ObjectStorageCompressionConfigurationProvider<T : OutputStream> {
    val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>
}
