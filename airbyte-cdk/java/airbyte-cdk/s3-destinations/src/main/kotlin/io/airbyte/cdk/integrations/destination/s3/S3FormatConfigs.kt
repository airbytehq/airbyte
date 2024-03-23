/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.avro.S3AvroFormatConfig
import io.airbyte.cdk.integrations.destination.s3.csv.S3CsvFormatConfig
import io.airbyte.cdk.integrations.destination.s3.jsonl.S3JsonlFormatConfig
import io.airbyte.cdk.integrations.destination.s3.parquet.S3ParquetFormatConfig
import io.airbyte.commons.json.Jsons
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

object S3FormatConfigs {
    internal val LOGGER: Logger = LoggerFactory.getLogger(S3FormatConfigs::class.java)

    @JvmStatic
    fun getS3FormatConfig(config: JsonNode): S3FormatConfig {
        val formatConfig = config["format"]
        LOGGER.info("S3 format config: {}", formatConfig.toString())
        val formatType =
            S3Format.valueOf(formatConfig["format_type"].asText().uppercase(Locale.getDefault()))

        return when (formatType) {
            S3Format.AVRO -> {
                S3AvroFormatConfig(formatConfig)
            }
            S3Format.CSV -> {
                S3CsvFormatConfig(formatConfig)
            }
            S3Format.JSONL -> {
                S3JsonlFormatConfig(formatConfig)
            }
            S3Format.PARQUET -> {
                S3ParquetFormatConfig(formatConfig)
            }
            else -> {
                throw RuntimeException("Unexpected output format: " + Jsons.serialize(config))
            }
        }
    }
}
