/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.avro

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import org.apache.avro.file.CodecFactory

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "codec"
)
@JsonSubTypes(
    JsonSubTypes.Type(
        value = AvroFormatNoCompressionCodecSpecification::class,
        name = "no compression"
    ),
    JsonSubTypes.Type(value = AvroFormatDeflateCodecSpecification::class, name = "Deflate"),
    JsonSubTypes.Type(value = AvroFormatBzip2CodecSpecification::class, name = "bzip2"),
    JsonSubTypes.Type(value = AvroFormatXzCodecSpecification::class, name = "xz"),
    JsonSubTypes.Type(value = AvroFormatZstandardCodecSpecification::class, name = "zstandard"),
    JsonSubTypes.Type(value = AvroFormatSnappyCodecSpecification::class, name = "snappy")
)
sealed class AvroFormatCompressionCodecSpecification(
    @JsonSchemaTitle("Compression Codec") @JsonProperty("codec") open val type: Type
) {
    enum class Type(@get:JsonValue val typeName: String) {
        NO_COMPRESSION("no compression"),
        DEFLATE("Deflate"),
        BZIP2("bzip2"),
        XZ("xz"),
        ZSTANDARD("zstandard"),
        SNAPPY("snappy")
    }

    fun toCompressionConfiguration() =
        AvroCompressionConfiguration(
            compressionCodec =
                when (this) {
                    is AvroFormatNoCompressionCodecSpecification -> CodecFactory.nullCodec()
                    is AvroFormatDeflateCodecSpecification ->
                        CodecFactory.deflateCodec(compressionLevel)
                    is AvroFormatBzip2CodecSpecification -> CodecFactory.bzip2Codec()
                    is AvroFormatXzCodecSpecification -> CodecFactory.xzCodec(compressionLevel)
                    is AvroFormatZstandardCodecSpecification ->
                        CodecFactory.zstandardCodec(compressionLevel, includeChecksum)
                    is AvroFormatSnappyCodecSpecification -> CodecFactory.snappyCodec()
                }
        )
}

data class AvroFormatNoCompressionCodecSpecification(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.NO_COMPRESSION,
) : AvroFormatCompressionCodecSpecification(type)

data class AvroFormatDeflateCodecSpecification(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.DEFLATE,
    @JsonSchemaTitle("Deflate Level")
    @JsonProperty("compression_level")
    val compressionLevel: Int = 0
) : AvroFormatCompressionCodecSpecification(type)

data class AvroFormatBzip2CodecSpecification(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.BZIP2,
) : AvroFormatCompressionCodecSpecification(type)

data class AvroFormatXzCodecSpecification(
    @JsonSchemaTitle("Compression Codec") @JsonProperty("codec") override val type: Type = Type.XZ,
    @JsonSchemaTitle("Compression Level")
    @JsonProperty("compression_level")
    val compressionLevel: Int = 6
) : AvroFormatCompressionCodecSpecification(type)

data class AvroFormatZstandardCodecSpecification(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.ZSTANDARD,
    @JsonSchemaTitle("Compression Level")
    @JsonProperty("compression_level")
    val compressionLevel: Int = 3,
    @JsonSchemaTitle("Include Checksum")
    @JsonProperty("include_checksum")
    val includeChecksum: Boolean = false
) : AvroFormatCompressionCodecSpecification(type)

data class AvroFormatSnappyCodecSpecification(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.SNAPPY,
) : AvroFormatCompressionCodecSpecification(type)

data class AvroCompressionConfiguration(val compressionCodec: CodecFactory)

interface AvroCompressionConfigurationProvider {
    val avroCompressionConfiguration: AvroCompressionConfiguration
}
