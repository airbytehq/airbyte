/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import java.io.Serializable

interface OutputFormatSpecificationProvider {
    @get:JsonSchemaTitle("Output Format")
    @get:JsonPropertyDescription(
        "Format of the data output. See <a href=\"https://docs.airbyte.com/integrations/destinations/s3/#supported-output-schema\">here</a> for more details",
    )
    val format: OutputFormatSpecification

    fun toOutputFormatConfiguration(): OutputFormatConfiguration {
        return when (format) {
            is JsonOutputFormatSpecification -> JsonOutputFormatConfiguration()
            is CSVOutputFormatSpecification -> CSVOutputFormatConfiguration()
            is AvroOutputFormatSpecification -> AvroOutputFormatConfiguration()
            is ParquetOutputFormatSpecification -> ParquetOutputFormatConfiguration()
        }
    }
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "format_type"
)
@JsonSubTypes(
    JsonSubTypes.Type(value = JsonOutputFormatSpecification::class, name = "JSONL"),
    JsonSubTypes.Type(value = CSVOutputFormatSpecification::class, name = "CSV"),
    JsonSubTypes.Type(value = AvroOutputFormatSpecification::class, name = "AVRO"),
    JsonSubTypes.Type(value = ParquetOutputFormatSpecification::class, name = "PARQUET")
)
sealed class OutputFormatSpecification {
    @JsonSchemaTitle("Format Type") @JsonProperty("format_type") val formatType: String = "JSONL"
}

@JsonSchemaTitle("JSON Lines: Newline-delimited JSON")
class JsonOutputFormatSpecification : OutputFormatSpecification()

@JsonSchemaTitle("CSV: Comma-Separated Values")
class CSVOutputFormatSpecification : OutputFormatSpecification()

@JsonSchemaTitle("Avro: Apache Avro")
class AvroOutputFormatSpecification : OutputFormatSpecification()

@JsonSchemaTitle("Parquet: Columnar Storage")
class ParquetOutputFormatSpecification : OutputFormatSpecification()

interface OutputFormatConfigurationProvider {
    val outputFormat: OutputFormatConfiguration
}

sealed interface OutputFormatConfiguration : Serializable {
    val extension: String
}

data class JsonOutputFormatConfiguration(override val extension: String = "jsonl") :
    OutputFormatConfiguration

data class CSVOutputFormatConfiguration(override val extension: String = "csv") :
    OutputFormatConfiguration

data class AvroOutputFormatConfiguration(override val extension: String = "avro") :
    OutputFormatConfiguration

data class ParquetOutputFormatConfiguration(override val extension: String = "parquet") :
    OutputFormatConfiguration
