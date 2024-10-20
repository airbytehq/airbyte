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
import io.airbyte.cdk.load.command.avro.AvroCompressionConfiguration
import io.airbyte.cdk.load.command.avro.AvroCompressionConfigurationProvider
import io.airbyte.cdk.load.command.avro.AvroFormatCompressionCodec
import io.airbyte.cdk.load.command.avro.AvroFormatNoCompressionCodec

/**
 * Mix-in to provide file format configuration.
 *
 * NOTE: This assumes a fixed set of file formats. If you need to support a different set, clone the
 * [ObjectStorageFormatSpecification] class with a new set of enums.
 *
 * See [io.airbyte.cdk.load.command.DestinationConfiguration] for more details on how to use this
 * interface.
 */
interface ObjectStorageFormatSpecificationProvider {
    @get:JsonSchemaTitle("Output Format")
    @get:JsonPropertyDescription(
        "Format of the data output. See <a href=\"https://docs.airbyte.com/integrations/destinations/s3/#supported-output-schema\">here</a> for more details",
    )
    @get:JsonProperty("format")
    val format: ObjectStorageFormatSpecification

    fun toObjectStorageFormatConfiguration(): ObjectStorageFormatConfiguration {
        return when (format) {
            is JsonFormatSpecification -> JsonFormatConfiguration()
            is CSVFormatSpecification -> CSVFormatConfiguration()
            is AvroFormatSpecification ->
                AvroFormatConfiguration(
                    avroCompressionConfiguration =
                        (format as AvroFormatSpecification)
                            .compressionCodec
                            .toCompressionConfiguration()
                )
            is ParquetFormatSpecification -> ParquetFormatConfiguration()
        }
    }

    fun toCompressionConfiguration(): ObjectStorageCompressionConfiguration<*> {
        return when (format) {
            is ObjectStorageCompressionSpecificationProvider ->
                (format as ObjectStorageCompressionSpecificationProvider)
                    .toCompressionConfiguration()
            else -> ObjectStorageCompressionSpecificationProvider.getNoCompressionConfiguration()
        }
    }
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "format_type"
)
@JsonSubTypes(
    JsonSubTypes.Type(value = JsonFormatSpecification::class, name = "JSONL"),
    JsonSubTypes.Type(value = CSVFormatSpecification::class, name = "CSV"),
    JsonSubTypes.Type(value = AvroFormatSpecification::class, name = "Avro"),
    JsonSubTypes.Type(value = ParquetFormatSpecification::class, name = "Parquet")
)
sealed class ObjectStorageFormatSpecification(
    @JsonSchemaTitle("Format Type") open val formatType: Type
) {
    enum class Type(@get:JsonValue val typeName: String) {
        JSONL("JSONL"),
        CSV("CSV"),
        AVRO("Avro"),
        PARQUET("Parquet")
    }
}

/** JSONL */
@JsonSchemaTitle("JSON Lines: Newline-delimited JSON")
class JsonFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.JSONL
) : ObjectStorageFormatSpecification(formatType), ObjectStorageCompressionSpecificationProvider {
    override val compression: ObjectStorageCompressionSpecification = NoCompressionSpecification()
}

/** CSV */
@JsonSchemaTitle("CSV: Comma-Separated Values")
class CSVFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.CSV
) : ObjectStorageFormatSpecification(formatType), ObjectStorageCompressionSpecificationProvider {
    override val compression: ObjectStorageCompressionSpecification = NoCompressionSpecification()
}

/** AVRO */
@JsonSchemaTitle("Avro: Apache Avro")
class AvroFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.AVRO
) : ObjectStorageFormatSpecification(formatType) {

    @JsonSchemaTitle("Compression Codec")
    @JsonPropertyDescription(
        "The compression algorithm used to compress data. Default to no compression."
    )
    @JsonProperty("compression_codec")
    val compressionCodec: AvroFormatCompressionCodec = AvroFormatNoCompressionCodec()
}

/** Parquet */
@JsonSchemaTitle("Parquet: Columnar Storage")
class ParquetFormatSpecification(
    @JsonProperty("format_type") override val formatType: Type = Type.PARQUET
) : ObjectStorageFormatSpecification(formatType)

/** Configuration */
interface OutputFormatConfigurationProvider {
    val outputFormat: ObjectStorageFormatConfiguration
}

sealed interface ObjectStorageFormatConfiguration {
    val extension: String
}

data class JsonFormatConfiguration(override val extension: String = "jsonl") :
    ObjectStorageFormatConfiguration

data class CSVFormatConfiguration(override val extension: String = "csv") :
    ObjectStorageFormatConfiguration

data class AvroFormatConfiguration(
    override val extension: String = "avro",
    override val avroCompressionConfiguration: AvroCompressionConfiguration,
) : ObjectStorageFormatConfiguration, AvroCompressionConfigurationProvider

data class ParquetFormatConfiguration(override val extension: String = "parquet") :
    ObjectStorageFormatConfiguration

interface ObjectStorageFormatConfigurationProvider {
    val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration
}
