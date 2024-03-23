/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.jsonl

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.S3Format
import io.airbyte.cdk.integrations.destination.s3.S3FormatConfig
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.CompressionTypeHelper
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.destination.s3.util.Flattening.Companion.fromValue
import java.util.*
import lombok.ToString

@ToString
class S3JsonlFormatConfig(val flatteningType: Flattening, val compressionType: CompressionType) :
    S3FormatConfig {
    constructor(
        formatConfig: JsonNode
    ) : this(
        if (formatConfig.has(S3DestinationConstants.FLATTENING_ARG_NAME))
            fromValue(formatConfig[S3DestinationConstants.FLATTENING_ARG_NAME].asText())
        else Flattening.NO,
        if (formatConfig.has(S3DestinationConstants.COMPRESSION_ARG_NAME))
            CompressionTypeHelper.parseCompressionType(
                formatConfig[S3DestinationConstants.COMPRESSION_ARG_NAME]
            )
        else S3DestinationConstants.DEFAULT_COMPRESSION_TYPE
    )

    override val format: S3Format = S3Format.JSONL

    override val fileExtension: String = JSONL_SUFFIX + compressionType.fileExtension

    override fun equals(o: Any?): Boolean {
        if (this === o) {
            return true
        }
        if (o == null || javaClass != o.javaClass) {
            return false
        }
        val that = o as S3JsonlFormatConfig
        return flatteningType == that.flatteningType && compressionType == that.compressionType
    }

    override fun hashCode(): Int {
        return Objects.hash(flatteningType, compressionType)
    }

    companion object {
        const val JSONL_SUFFIX: String = ".jsonl"
    }
}
