/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfig
import org.apache.avro.file.CodecFactory

class UploadAvroFormatConfig : UploadFormatConfig {
    val codecFactory: CodecFactory

    override val fileExtension: String = DEFAULT_SUFFIX

    constructor(codecFactory: CodecFactory) {
        this.codecFactory = codecFactory
    }

    constructor(formatConfig: JsonNode) {
        this.codecFactory = parseCodecConfig(formatConfig["compression_codec"])
    }

    override val format: FileUploadFormat
        get() = FileUploadFormat.AVRO

    enum class CompressionCodec(private val configValue: String) {
        NULL("no compression"),
        DEFLATE("deflate"),
        BZIP2("bzip2"),
        XZ("xz"),
        ZSTANDARD("zstandard"),
        SNAPPY("snappy");

        companion object {
            fun fromConfigValue(configValue: String): CompressionCodec {
                for (codec in entries) {
                    if (configValue.equals(codec.configValue, ignoreCase = true)) {
                        return codec
                    }
                }
                throw IllegalArgumentException("Unknown codec config value: $configValue")
            }
        }
    }

    companion object {
        @JvmStatic val DEFAULT_SUFFIX: String = ".avro"

        @JvmStatic
        fun parseCodecConfig(compressionCodecConfig: JsonNode?): CodecFactory {
            if (compressionCodecConfig == null || compressionCodecConfig.isNull) {
                return CodecFactory.nullCodec()
            }

            val codecConfig = compressionCodecConfig["codec"]
            if (codecConfig == null || codecConfig.isNull || !codecConfig.isTextual) {
                return CodecFactory.nullCodec()
            }
            val codecType = codecConfig.asText()
            val codec = CompressionCodec.fromConfigValue(codecConfig.asText())
            when (codec) {
                CompressionCodec.NULL -> {
                    return CodecFactory.nullCodec()
                }
                CompressionCodec.DEFLATE -> {
                    val compressionLevel = getCompressionLevel(compressionCodecConfig, 0, 0, 9)
                    return CodecFactory.deflateCodec(compressionLevel)
                }
                CompressionCodec.BZIP2 -> {
                    return CodecFactory.bzip2Codec()
                }
                CompressionCodec.XZ -> {
                    val compressionLevel = getCompressionLevel(compressionCodecConfig, 6, 0, 9)
                    return CodecFactory.xzCodec(compressionLevel)
                }
                CompressionCodec.ZSTANDARD -> {
                    val compressionLevel = getCompressionLevel(compressionCodecConfig, 3, -5, 22)
                    val includeChecksum = getIncludeChecksum(compressionCodecConfig, false)
                    return CodecFactory.zstandardCodec(compressionLevel, includeChecksum)
                }
                CompressionCodec.SNAPPY -> {
                    return CodecFactory.snappyCodec()
                }
                else -> {
                    throw IllegalArgumentException("Unsupported compression codec: $codecType")
                }
            }
        }

        fun getCompressionLevel(
            compressionCodecConfig: JsonNode,
            defaultLevel: Int,
            minLevel: Int,
            maxLevel: Int
        ): Int {
            val levelConfig = compressionCodecConfig["compression_level"]
            if (levelConfig == null || levelConfig.isNull || !levelConfig.isIntegralNumber) {
                return defaultLevel
            }
            val level = levelConfig.asInt()
            require(!(level < minLevel || level > maxLevel)) {
                String.format(
                    "Invalid compression level: %d, expected an integer in range [%d, %d]",
                    level,
                    minLevel,
                    maxLevel
                )
            }
            return level
        }

        fun getIncludeChecksum(compressionCodecConfig: JsonNode, defaultValue: Boolean): Boolean {
            val checksumConfig = compressionCodecConfig["include_checksum"]
            if (checksumConfig == null || checksumConfig.isNumber || !checksumConfig.isBoolean) {
                return defaultValue
            }
            return checksumConfig.asBoolean()
        }
    }
}
