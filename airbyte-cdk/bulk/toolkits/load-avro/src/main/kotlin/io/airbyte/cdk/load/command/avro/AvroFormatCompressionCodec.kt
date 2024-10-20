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
    JsonSubTypes.Type(value = AvroFormatNoCompressionCodec::class, name = "no compression"),
    JsonSubTypes.Type(value = AvroFormatDeflateCodec::class, name = "Deflate"),
    JsonSubTypes.Type(value = AvroFormatBzip2Codec::class, name = "bzip2"),
    JsonSubTypes.Type(value = AvroFormatXzCodec::class, name = "xz"),
    JsonSubTypes.Type(value = AvroFormatZstandardCodec::class, name = "zstandard"),
    JsonSubTypes.Type(value = AvroFormatSnappyCodec::class, name = "snappy")
)
sealed class AvroFormatCompressionCodec(
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
                    is AvroFormatNoCompressionCodec -> CodecFactory.nullCodec()
                    is AvroFormatDeflateCodec -> CodecFactory.deflateCodec(compressionLevel)
                    is AvroFormatBzip2Codec -> CodecFactory.bzip2Codec()
                    is AvroFormatXzCodec -> CodecFactory.xzCodec(compressionLevel)
                    is AvroFormatZstandardCodec ->
                        CodecFactory.zstandardCodec(compressionLevel, includeChecksum)
                    is AvroFormatSnappyCodec -> CodecFactory.snappyCodec()
                }
        )
}

data class AvroFormatNoCompressionCodec(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.NO_COMPRESSION,
) : AvroFormatCompressionCodec(type)

data class AvroFormatDeflateCodec(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.DEFLATE,
    @JsonSchemaTitle("Deflate Level")
    @JsonProperty("compression_level")
    val compressionLevel: Int = 0
) : AvroFormatCompressionCodec(type)

data class AvroFormatBzip2Codec(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.BZIP2,
) : AvroFormatCompressionCodec(type)

data class AvroFormatXzCodec(
    @JsonSchemaTitle("Compression Codec") @JsonProperty("codec") override val type: Type = Type.XZ,
    @JsonSchemaTitle("Compression Level")
    @JsonProperty("compression_level")
    val compressionLevel: Int = 6
) : AvroFormatCompressionCodec(type)

data class AvroFormatZstandardCodec(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.ZSTANDARD,
    @JsonSchemaTitle("Compression Level")
    @JsonProperty("compression_level")
    val compressionLevel: Int = 3,
    @JsonSchemaTitle("Include Checksum")
    @JsonProperty("include_checksum")
    val includeChecksum: Boolean = false
) : AvroFormatCompressionCodec(type)

data class AvroFormatSnappyCodec(
    @JsonSchemaTitle("Compression Codec")
    @JsonProperty("codec")
    override val type: Type = Type.SNAPPY,
) : AvroFormatCompressionCodec(type)

data class AvroCompressionConfiguration(val compressionCodec: CodecFactory)

interface AvroCompressionConfigurationProvider {
    val avroCompressionConfiguration: AvroCompressionConfiguration
}
