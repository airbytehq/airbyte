/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.avro.AvroFormatCompressionCodecSpecification
import io.airbyte.cdk.load.command.avro.AvroFormatNoCompressionCodecSpecification
import io.airbyte.cdk.load.file.parquet.ParquetWriterConfiguration

/**
 * Mix-in to provide file format configuration.
 *
 * NOTE: This assumes a fixed set of file formats. If you need to support a different set, clone the
 * [DeprecatedObjectStorageFormatSpecification] class with a new set of enums.
 *
 * See [io.airbyte.cdk.load.command.DestinationConfiguration] for more details on how to use this
 * interface.
 *
 * This class has been deprecated. The Avro and Parquet formats from this class exist to support the
 * legacy S3 destination, in the future if we add avro and parquet back we will add back a less
 * complicated version
 */
interface DeprecatedObjectStorageFormatSpecificationProvider {
    @get:JsonSchemaTitle("Output Format")
    @get:JsonPropertyDescription(
        "Format of the data output. See <a href=\"https://docs.airbyte.com/integrations/destinations/s3/#supported-output-schema\">here</a> for more details",
    )
    @get:JsonProperty("format")
    val format: DeprecatedObjectStorageFormatSpecification

    fun toObjectStorageFormatConfiguration(): ObjectStorageFormatConfiguration {
        return when (format) {
            is DeprecatedJsonFormatSpecification ->
                JsonFormatConfiguration(
                    rootLevelFlattening =
                        (format as DeprecatedJsonFormatSpecification).flattening ==
                            FlatteningSpecificationProvider.Flattening.ROOT_LEVEL_FLATTENING
                )
            is DeprecatedCSVFormatSpecification ->
                CSVFormatConfiguration(
                    rootLevelFlattening =
                        (format as DeprecatedCSVFormatSpecification).flattening ==
                            FlatteningSpecificationProvider.Flattening.ROOT_LEVEL_FLATTENING
                )
            is DeprecatedAvroFormatSpecification ->
                AvroFormatConfiguration(
                    avroCompressionConfiguration =
                        (format as DeprecatedAvroFormatSpecification)
                            .compressionCodec
                            .toCompressionConfiguration()
                )
            is DeprecatedParquetFormatSpecification -> {
                (format as DeprecatedParquetFormatSpecification).let {
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
    JsonSubTypes.Type(value = DeprecatedCSVFormatSpecification::class, name = "CSV"),
    JsonSubTypes.Type(value = DeprecatedJsonFormatSpecification::class, name = "JSONL"),
    JsonSubTypes.Type(value = DeprecatedAvroFormatSpecification::class, name = "Avro"),
    JsonSubTypes.Type(value = DeprecatedParquetFormatSpecification::class, name = "Parquet")
)
sealed class DeprecatedObjectStorageFormatSpecification(
    @JsonSchemaTitle("Format Type") open val formatType: Type
) {
    enum class Type(@get:JsonValue val typeName: String) {
        CSV("CSV"),
        JSONL("JSONL"),
        AVRO("Avro"),
        PARQUET("Parquet")
    }
}

/** CSV */
@JsonSchemaTitle("CSV: Comma-Separated Values")
class DeprecatedCSVFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.CSV
) :
    DeprecatedObjectStorageFormatSpecification(formatType),
    FlatteningSpecificationProvider,
    ObjectStorageCompressionSpecificationProvider {
    override val flattening: FlatteningSpecificationProvider.Flattening =
        FlatteningSpecificationProvider.Flattening.NO_FLATTENING
    override val compression: ObjectStorageCompressionSpecification? =
        GZIPCompressionSpecification()
}

/** JSONL */
@JsonSchemaTitle("JSON Lines: Newline-delimited JSON")
class DeprecatedJsonFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.JSONL
) :
    DeprecatedObjectStorageFormatSpecification(formatType),
    FlatteningSpecificationProvider,
    ObjectStorageCompressionSpecificationProvider {
    override val flattening: FlatteningSpecificationProvider.Flattening? =
        FlatteningSpecificationProvider.Flattening.NO_FLATTENING
    override val compression: ObjectStorageCompressionSpecification? =
        GZIPCompressionSpecification()
}

/** AVRO */
@JsonSchemaTitle("Avro: Apache Avro")
class DeprecatedAvroFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    @JsonSchemaInject(json = """{"order":0}""")
    override val formatType: Type = Type.AVRO
) : DeprecatedObjectStorageFormatSpecification(formatType) {

    @JsonSchemaTitle("Compression Codec")
    @JsonPropertyDescription(
        "The compression algorithm used to compress data. Default to no compression."
    )
    @JsonProperty("compression_codec")
    @JsonSchemaInject(json = """{"order":1}""")
    val compressionCodec: AvroFormatCompressionCodecSpecification =
        AvroFormatNoCompressionCodecSpecification()
}

/** Parquet */
@JsonSchemaTitle("Parquet: Columnar Storage")
class DeprecatedParquetFormatSpecification(
    @JsonSchemaTitle("Format Type")
    @JsonProperty("format_type")
    override val formatType: Type = Type.PARQUET
) : DeprecatedObjectStorageFormatSpecification(formatType) {
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
    @JsonProperty("compression_codec", defaultValue = "UNCOMPRESSED")
    val compressionCodec: ParquetFormatCompressionCodec? =
        ParquetFormatCompressionCodec.UNCOMPRESSED

    @JsonSchemaTitle("Block Size (Row Group Size) (MB)")
    @JsonPropertyDescription(
        "This is the size of a row group being buffered in memory. It limits the memory usage when writing. Larger values will improve the IO when reading, but consume more memory when writing. Default: 128 MB."
    )
    @JsonProperty("block_size_mb", defaultValue = "128")
    val blockSizeMb: Int? = 128

    @JsonSchemaTitle("Max Padding Size (MB)")
    @JsonPropertyDescription(
        "Maximum size allowed as padding to align row groups. This is also the minimum size of a row group. Default: 8 MB."
    )
    @JsonProperty("max_padding_size_mb", defaultValue = "8")
    val maxPaddingSizeMb: Int? = 8

    @JsonSchemaTitle("Page Size (KB)")
    @JsonPropertyDescription(
        "The page size is for compression. A block is composed of pages. A page is the smallest unit that must be read fully to access a single record. If this value is too small, the compression will deteriorate. Default: 1024 KB."
    )
    @JsonProperty("page_size_kb", defaultValue = "1024")
    val pageSizeKb: Int? = 1024

    @JsonSchemaTitle("Dictionary Page Size (KB)")
    @JsonPropertyDescription(
        "There is one dictionary page per column per row group when dictionary encoding is used. The dictionary page size works like the page size but for dictionary. Default: 1024 KB."
    )
    @JsonProperty("dictionary_page_size_kb", defaultValue = "1024")
    val dictionaryPageSizeKb: Int? = 1024

    @JsonSchemaTitle("Dictionary Encoding")
    @JsonPropertyDescription("Default: true.")
    @JsonProperty("dictionary_encoding")
    val dictionaryEncoding: Boolean? = true
}
