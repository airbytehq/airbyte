/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import java.util.*

object CompressionTypeHelper {
    /** Sample expected input: { "compression_type": "No Compression" } */
    @JvmStatic
    fun parseCompressionType(compressionConfig: JsonNode?): CompressionType {
        if (compressionConfig == null || compressionConfig.isNull) {
            return S3DestinationConstants.DEFAULT_COMPRESSION_TYPE
        }
        val compressionType =
            compressionConfig[S3DestinationConstants.COMPRESSION_TYPE_ARG_NAME].asText()
        return if (compressionType.uppercase(Locale.getDefault()) == CompressionType.GZIP.name) {
            CompressionType.GZIP
        } else {
            CompressionType.NO_COMPRESSION
        }
    }
}
