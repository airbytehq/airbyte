/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.jackson.MoreMappers
import org.junit.jupiter.api.Assertions.assertLinesMatch
import org.junit.jupiter.api.Test

class NoFlatteningSheetGeneratorTest {

    private val mapper: ObjectMapper = MoreMappers.initMapper()
    private val sheetGenerator = NoFlatteningSheetGenerator()

    @Test
    internal fun testGetHeaderRow() {
        assertLinesMatch(
            listOf(
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
                JavaBaseConstants.COLUMN_NAME_DATA,
            ),
            sheetGenerator.getHeaderRow(),
        )
    }

    @Test
    internal fun testGetRecordColumns() {
        val json = mapper.createObjectNode()
        json.set<JsonNode>("Field 4", mapper.createObjectNode().put("Field 41", 15))
        json.put("Field 1", "A")
        json.put("Field 3", 71)
        json.put("Field 2", true)

        assertLinesMatch(
            listOf(
                "{\"Field 4\":{\"Field 41\":15},\"Field 1\":\"A\",\"Field 3\":71,\"Field 2\":true}"
            ),
            sheetGenerator.getRecordColumns(json),
        )
    }
}
