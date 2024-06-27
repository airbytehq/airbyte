/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.staging

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSheetGenerator
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.time.Instant
import java.util.*
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.QuoteMode

/**
 * This is identical to
 * [io.airbyte.cdk.integrations.destination.staging.StagingSerializedBufferFactory] but the
 * getDataRow excludes including a blank value for _airbyte_loaded_at field. Databricks CSV load was
 * failing with empty field in CSV.
 */
object DatabricksFileBufferFactory {
    /** Factory function to create buffer based on format */
    fun createBuffer(fileUploadFormat: FileUploadFormat): SerializableBuffer {
        when (fileUploadFormat) {
            FileUploadFormat.AVRO -> TODO()
            FileUploadFormat.CSV -> {
                val csvSheetGenerator =
                    object : CsvSheetGenerator {
                        override fun getHeaderRow(): List<String> {
                            return listOf(
                                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                                JavaBaseConstants.COLUMN_NAME_DATA,
                                JavaBaseConstants.COLUMN_NAME_AB_META
                            )
                        }

                        override fun getDataRow(
                            id: UUID,
                            recordMessage: AirbyteRecordMessage
                        ): List<Any> {
                            TODO("Not yet implemented")
                        }

                        override fun getDataRow(formattedData: JsonNode): List<Any> {
                            TODO("Not yet implemented")
                        }

                        override fun getDataRow(
                            id: UUID,
                            formattedString: String,
                            emittedAt: Long,
                            formattedAirbyteMetaString: String
                        ): List<Any> {
                            return listOf(
                                id,
                                Instant.ofEpochMilli(emittedAt),
                                formattedString,
                                formattedAirbyteMetaString
                            )
                        }
                    }
                val csvSettings =
                    CSVFormat.Builder.create()
                        .setQuoteMode(QuoteMode.NON_NUMERIC)
                        .setHeader(*csvSheetGenerator.getHeaderRow().toTypedArray<String>())
                        .build()
                return CsvSerializedBuffer(
                        FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
                        csvSheetGenerator,
                        true,
                    )
                    .withCsvFormat(csvSettings)
            }
            FileUploadFormat.JSONL -> TODO()
            FileUploadFormat.PARQUET -> TODO()
        }
    }
}
