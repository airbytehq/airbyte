/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.avro.UploadAvroFormatConfig
import io.airbyte.cdk.integrations.destination.s3.csv.UploadCsvFormatConfig
import io.airbyte.cdk.integrations.destination.s3.jsonl.UploadJsonlFormatConfig
import io.airbyte.cdk.integrations.destination.s3.parquet.UploadParquetFormatConfig
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*

private val LOGGER = KotlinLogging.logger {}

object UploadFormatConfigFactory {

    fun getUploadFormatConfig(config: JsonNode): UploadFormatConfig {
        val formatConfig = config["format"]
        LOGGER.info { "File upload format config: $formatConfig" }
        val formatType =
            FileUploadFormat.valueOf(
                formatConfig["format_type"].asText().uppercase(Locale.getDefault())
            )

        return when (formatType) {
            FileUploadFormat.AVRO -> {
                UploadAvroFormatConfig(formatConfig)
            }
            FileUploadFormat.CSV -> {
                UploadCsvFormatConfig(formatConfig)
            }
            FileUploadFormat.JSONL -> {
                UploadJsonlFormatConfig(formatConfig)
            }
            FileUploadFormat.PARQUET -> {
                UploadParquetFormatConfig(formatConfig)
            }
        }
    }
}
