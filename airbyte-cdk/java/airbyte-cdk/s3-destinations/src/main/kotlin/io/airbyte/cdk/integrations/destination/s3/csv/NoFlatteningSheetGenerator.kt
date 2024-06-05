/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons

class NoFlatteningSheetGenerator : BaseSheetGenerator(), CsvSheetGenerator {
    override fun getHeaderRow(): List<String> {
        return listOf(
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            JavaBaseConstants.COLUMN_NAME_DATA,
        )
    }

    /** When no flattening is needed, the record column is just one json blob. */
    override fun getRecordColumns(json: JsonNode): List<String> {
        return listOf(Jsons.serialize(json))
    }
}
