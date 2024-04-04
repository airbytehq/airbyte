/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.config.properties

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.integrations.destination.s3.avro.S3AvroFormatConfig.CompressionCodec
import io.micronaut.core.util.StringUtils

class S3CompressionCodec(compressionCodec: Map<String, Any?>) {

    @JsonProperty("codec")
    val codec: String = compressionCodec.getOrDefault("codec", CompressionCodec.NULL.name).toString()

    @JsonProperty("compression_level")
    val compressionLevel: String = compressionCodec.getOrDefault("compression_level", "").toString()

    @JsonProperty("include_checksum")
    val includeChecksum: Boolean = compressionCodec.getOrDefault("include_checksum", false) as Boolean

    fun getCodec(): CompressionCodec {
        return CompressionCodec.valueOf(codec)
    }

    fun getCompressionLevel(defaultLevel: Int, minLevel: Int, maxLevel: Int): Int {
        if (StringUtils.isEmpty(compressionLevel)) {
            return defaultLevel
        }
        val level = compressionLevel as Int
        require(!(level < minLevel || level > maxLevel)) {
            "Invalid compression level: $level, expected an integer in range [$minLevel, $maxLevel]"
        }
        return level
    }
}
