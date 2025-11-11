/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfig
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.CompressionTypeHelper
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.destination.s3.util.Flattening.Companion.fromValue
import java.util.*

class UploadCsvFormatConfig(val flattening: Flattening, val compressionType: CompressionType) :
    UploadFormatConfig {
    constructor(
        formatConfig: JsonNode
    ) : this(
        fromValue(
            if (formatConfig.has("flattening")) formatConfig["flattening"].asText()
            else Flattening.NO.value
        ),
        if (formatConfig.has(S3DestinationConstants.COMPRESSION_ARG_NAME))
            CompressionTypeHelper.parseCompressionType(
                formatConfig[S3DestinationConstants.COMPRESSION_ARG_NAME]
            )
        else S3DestinationConstants.DEFAULT_COMPRESSION_TYPE
    )

    override val format: FileUploadFormat = FileUploadFormat.CSV

    override val fileExtension: String = CSV_SUFFIX + compressionType.fileExtension

    override fun toString(): String {
        return "S3CsvFormatConfig{" +
            "flattening=" +
            flattening +
            ", compression=" +
            compressionType.name +
            '}'
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as UploadCsvFormatConfig
        return flattening == that.flattening && compressionType == that.compressionType
    }

    override fun hashCode(): Int {
        return Objects.hash(flattening, compressionType)
    }

    companion object {
        const val CSV_SUFFIX: String = ".csv"
    }
}
