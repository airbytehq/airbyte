/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.jsonl

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfig
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.CompressionTypeHelper
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.destination.s3.util.Flattening.Companion.fromValue
import java.util.*
import org.apache.commons.lang3.builder.ToStringBuilder

class UploadJsonlFormatConfig(
    val flatteningType: Flattening,
    val compressionType: CompressionType
) : UploadFormatConfig {
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

    override val format: FileUploadFormat = FileUploadFormat.JSONL

    override val fileExtension: String = JSONL_SUFFIX + compressionType.fileExtension

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as UploadJsonlFormatConfig
        return flatteningType == that.flatteningType && compressionType == that.compressionType
    }

    override fun hashCode(): Int {
        return Objects.hash(flatteningType, compressionType)
    }

    override fun toString(): String {
        return ToStringBuilder.reflectionToString(this)
    }

    companion object {
        const val JSONL_SUFFIX: String = ".jsonl"
    }
}
