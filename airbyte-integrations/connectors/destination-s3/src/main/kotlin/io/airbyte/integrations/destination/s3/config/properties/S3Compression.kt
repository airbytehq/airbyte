/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.config.properties

import com.fasterxml.jackson.annotation.JsonProperty

class S3Compression(compression: Map<String, String>) {
    @JsonProperty("compression_type")
    var compressionType: String = compression.getOrDefault("compression_type", "")
}
