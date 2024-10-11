/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

interface ObjectStorageFormatSpecificationProvider {
    @get:JsonSchemaTitle("Output Format")
    @get:JsonPropertyDescription(
        "Format of the data output. See <a href=\"https://docs.airbyte.com/integrations/destinations/s3/#supported-output-schema\">here</a> for more details",
    )
    val format: ObjectStorageFormatSpecification

    fun toObjectStorageFormatConfiguration(): ObjectStorageFormatConfiguration {
        return when (format) {
            is JsonFormatSpecification -> JsonFormatConfiguration()
            is CSVFormatSpecification -> CSVFormatConfiguration()
            is AvroFormatSpecification -> AvroFormatConfiguration()
            is ParquetFormatSpecification -> ParquetFormatConfiguration()
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
    JsonSubTypes.Type(value = AvroFormatSpecification::class, name = "AVRO"),
    JsonSubTypes.Type(value = ParquetFormatSpecification::class, name = "PARQUET")
)
sealed class ObjectStorageFormatSpecification {
    @JsonSchemaTitle("Format Type") @JsonProperty("format_type") val formatType: String = "JSONL"
}

@JsonSchemaTitle("JSON Lines: Newline-delimited JSON")
class JsonFormatSpecification : ObjectStorageFormatSpecification()

@JsonSchemaTitle("CSV: Comma-Separated Values")
class CSVFormatSpecification : ObjectStorageFormatSpecification()

@JsonSchemaTitle("Avro: Apache Avro")
class AvroFormatSpecification : ObjectStorageFormatSpecification()

@JsonSchemaTitle("Parquet: Columnar Storage")
class ParquetFormatSpecification : ObjectStorageFormatSpecification()

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

data class AvroFormatConfiguration(override val extension: String = "avro") :
    ObjectStorageFormatConfiguration

data class ParquetFormatConfiguration(override val extension: String = "parquet") :
    ObjectStorageFormatConfiguration

interface ObjectStorageFormatConfigurationProvider {
    val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration
}
