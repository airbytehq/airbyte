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
import io.airbyte.cdk.load.command.avro.AvroFormatCompressionCodecSpecification
import io.airbyte.cdk.load.command.avro.AvroFormatNoCompressionCodecSpecification
import io.airbyte.cdk.load.file.parquet.ParquetWriterConfiguration
import io.airbyte.cdk.load.file.parquet.ParquetWriterConfigurationProvider

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
            is ParquetFormatSpecification -> {
                (format as ParquetFormatSpecification).let {
                    ParquetFormatConfiguration(
                        parquetWriterConfiguration =
                            ParquetWriterConfiguration(
                                compressionCodecName = it.compressionCodec!!.name,
                                blockSizeMb = it.blockSizeMb!!,
                                maxPaddingSizeMb = it.maxPaddingSizeMb!!,
                                pageSizeKb = it.pageSizeKb!!,
                                dictionaryPageSizeKb = it.dictionaryPageSizeKb!!,
                                dictionaryEncoding = it.dictionaryEncoding!!
                            )
                    )
                }
            }
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
    val compressionCodec: AvroFormatCompressionCodecSpecification =
        AvroFormatNoCompressionCodecSpecification()
}

/** Parquet */
@JsonSchemaTitle("Parquet: Columnar Storage")
class ParquetFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.PARQUET
) : ObjectStorageFormatSpecification(formatType) {
    enum class ParquetFormatCompressionCodec {
        UNCOMPRESSED,
        SNAPPY,
        GZIP,
        LZO,
        BROTLI, // TODO: Broken locally in both this and s3 v1; Validate whether it works in prod
        LZ4,
        ZSTD
    }

    @JsonSchemaTitle("Compression Codec")
    @JsonPropertyDescription("The compression algorithm used to compress data pages.")
    @JsonProperty("compression_codec")
    val compressionCodec: ParquetFormatCompressionCodec? =
        ParquetFormatCompressionCodec.UNCOMPRESSED

    @JsonSchemaTitle("Block Size (Row Group Size) (MB)")
    @JsonPropertyDescription(
        "This is the size of a row group being buffered in memory. It limits the memory usage when writing. Larger values will improve the IO when reading, but consume more memory when writing. Default: 128 MB."
    )
    @JsonProperty("block_size_mb")
    val blockSizeMb: Int? = 128

    @JsonSchemaTitle("Max Padding Size (MB)")
    @JsonPropertyDescription(
        "Maximum size allowed as padding to align row groups. This is also the minimum size of a row group. Default: 8 MB."
    )
    @JsonProperty("max_padding_size_mb")
    val maxPaddingSizeMb: Int? = 8

    @JsonSchemaTitle("Page Size (KB)")
    @JsonPropertyDescription(
        "The page size is for compression. A block is composed of pages. A page is the smallest unit that must be read fully to access a single record. If this value is too small, the compression will deteriorate. Default: 1024 KB."
    )
    @JsonProperty("page_size_kb")
    val pageSizeKb: Int? = 1024

    @JsonSchemaTitle("Dictionary Page Size (KB)")
    @JsonPropertyDescription(
        "There is one dictionary page per column per row group when dictionary encoding is used. The dictionary page size works like the page size but for dictionary. Default: 1024 KB."
    )
    @JsonProperty("dictionary_page_size_kb")
    val dictionaryPageSizeKb: Int? = 1024

    @JsonSchemaTitle("Dictionary Encoding")
    @JsonPropertyDescription("Default: true.")
    @JsonProperty("dictionary_encoding")
    val dictionaryEncoding: Boolean? = true
}

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

data class ParquetFormatConfiguration(
    override val extension: String = "parquet",
    override val parquetWriterConfiguration: ParquetWriterConfiguration
) : ObjectStorageFormatConfiguration, ParquetWriterConfigurationProvider

interface ObjectStorageFormatConfigurationProvider {
    val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration
}
