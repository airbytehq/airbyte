/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.config.properties

import com.fasterxml.jackson.annotation.JsonProperty

class S3CompressionCodec(compressionCodec: Map<String, Any?>) {
    val codec: String = compressionCodec.getOrDefault("codec", "").toString()

    @JsonProperty("compression_level")
    val compressionLevel: String = compressionCodec.getOrDefault("compression_level", "").toString()

    @JsonProperty("include_checksum")
    val includeChecksum: Boolean = compressionCodec.getOrDefault("include_checksum", false) as Boolean
}
