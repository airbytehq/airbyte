/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.*

/**
 * This class takes case of the generation of the CSV data sheet, including the header row and the
 * data row.
 */
interface CsvSheetGenerator {
    fun getHeaderRow(): List<String>

    // TODO: (ryankfu) remove this and switch over all destinations to pass in serialized
    // recordStrings,
    // both for performance and lowers memory footprint
    fun getDataRow(
        id: UUID,
        recordMessage: AirbyteRecordMessage,
        generationId: Long = 0,
        syncId: Long = 0
    ): List<Any>

    fun getDataRow(formattedData: JsonNode): List<Any>

    fun getDataRow(
        id: UUID,
        formattedString: String,
        emittedAt: Long,
        formattedAirbyteMetaString: String,
        generationId: Long,
    ): List<Any>

    object Factory {
        @JvmStatic
        fun create(
            jsonSchema: JsonNode?,
            formatConfig: UploadCsvFormatConfig,
            useV2FieldNames: Boolean = false
        ): CsvSheetGenerator {
            return if (formatConfig.flattening == Flattening.NO) {
                NoFlatteningSheetGenerator(useV2FieldNames)
            } else if (formatConfig.flattening == Flattening.ROOT_LEVEL) {
                RootLevelFlatteningSheetGenerator(jsonSchema!!, useV2FieldNames)
            } else {
                throw IllegalArgumentException(
                    "Unexpected flattening config: " + formatConfig.flattening
                )
            }
        }
    }
}
