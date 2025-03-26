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
import io.airbyte.cdk.load.file.parquet.ParquetWriterConfiguration
import io.airbyte.cdk.load.file.parquet.ParquetWriterConfigurationProvider

interface ObjectStorageFormatSpecificationProvider {
    @get:JsonSchemaTitle("Output Format")
    @get:JsonPropertyDescription(
        "Format of the data output.",
    )
    @get:JsonProperty("format")
    val format: ObjectStorageFormatSpecification

    fun toObjectStorageFormatConfiguration(): ObjectStorageFormatConfiguration {
        return when (format) {
            is JsonFormatSpecification ->
                JsonFormatConfiguration(
                    rootLevelFlattening =
                        (format as JsonFormatSpecification).flattening ==
                            FlatteningSpecificationProvider.Flattening.ROOT_LEVEL_FLATTENING
                )
            is CSVFormatSpecification ->
                CSVFormatConfiguration(
                    rootLevelFlattening =
                        (format as CSVFormatSpecification).flattening ==
                            FlatteningSpecificationProvider.Flattening.ROOT_LEVEL_FLATTENING
                )
        }
    }
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "format_type"
)
@JsonSubTypes(
    JsonSubTypes.Type(value = CSVFormatSpecification::class, name = "CSV"),
    JsonSubTypes.Type(value = JsonFormatSpecification::class, name = "JSONL"),
)
sealed class ObjectStorageFormatSpecification(
    @JsonSchemaTitle("Format Type") open val formatType: Type
) {
    enum class Type(@get:JsonValue val typeName: String) {
        CSV("CSV"),
        JSONL("JSONL"),
    }
}

/** CSV */
@JsonSchemaTitle("CSV: Comma-Separated Values")
class CSVFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.CSV
) :
    ObjectStorageFormatSpecification(formatType),
    FlatteningSpecificationProvider,
    ObjectStorageCompressionSpecificationProvider {
    override val flattening: FlatteningSpecificationProvider.Flattening =
        FlatteningSpecificationProvider.Flattening.NO_FLATTENING
    override val compression: ObjectStorageCompressionSpecification? =
        GZIPCompressionSpecification()
}

/** JSONL */
@JsonSchemaTitle("JSON Lines: Newline-delimited JSON")
class JsonFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.JSONL
) :
    ObjectStorageFormatSpecification(formatType),
    FlatteningSpecificationProvider,
    ObjectStorageCompressionSpecificationProvider {
    override val flattening: FlatteningSpecificationProvider.Flattening? =
        FlatteningSpecificationProvider.Flattening.NO_FLATTENING
    override val compression: ObjectStorageCompressionSpecification? =
        GZIPCompressionSpecification()
}

interface FlatteningSpecificationProvider {
    @get:JsonSchemaTitle("Flattening")
    @get:JsonProperty("flattening", defaultValue = "No flattening")
    val flattening: Flattening?

    enum class Flattening(@get:JsonValue val flatteningName: String) {
        NO_FLATTENING("No flattening"),
        ROOT_LEVEL_FLATTENING("Root level flattening")
    }
}

/** Configuration */
interface OutputFormatConfigurationProvider {
    val outputFormat: ObjectStorageFormatConfiguration
}

sealed interface ObjectStorageFormatConfiguration {
    val extension: String
    val rootLevelFlattening: Boolean
}

data class JsonFormatConfiguration(
    override val extension: String = "jsonl",
    override val rootLevelFlattening: Boolean = false
) : ObjectStorageFormatConfiguration {}

data class CSVFormatConfiguration(
    override val extension: String = "csv",
    override val rootLevelFlattening: Boolean = false
) : ObjectStorageFormatConfiguration {}

data class AvroFormatConfiguration(
    override val extension: String = "avro",
    override val avroCompressionConfiguration: AvroCompressionConfiguration,
) : ObjectStorageFormatConfiguration, AvroCompressionConfigurationProvider {
    override val rootLevelFlattening: Boolean = true // Always flatten avro
}

data class ParquetFormatConfiguration(
    override val extension: String = "parquet",
    override val parquetWriterConfiguration: ParquetWriterConfiguration
) : ObjectStorageFormatConfiguration, ParquetWriterConfigurationProvider {
    override val rootLevelFlattening: Boolean = true // Always flatten parquet
}

interface ObjectStorageFormatConfigurationProvider {
    val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration
}
