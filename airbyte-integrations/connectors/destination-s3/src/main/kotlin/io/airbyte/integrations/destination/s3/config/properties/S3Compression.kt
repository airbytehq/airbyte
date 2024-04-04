/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.config.properties

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType

class S3Compression(compression: Map<String, String>) {

    @JsonProperty("compression_type")
    var compressionType: String = compression.getOrDefault("compression_type", CompressionType.NO_COMPRESSION.name)

    fun getCompressionType(): CompressionType {
        return CompressionType.valueOf(compressionType)
    }
}
