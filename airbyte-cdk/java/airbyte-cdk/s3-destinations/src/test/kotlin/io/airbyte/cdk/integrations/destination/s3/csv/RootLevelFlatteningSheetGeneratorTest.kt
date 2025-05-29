/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.jackson.MoreMappers
import org.junit.jupiter.api.Assertions.assertLinesMatch
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class RootLevelFlatteningSheetGeneratorTest {

    private lateinit var sheetGenerator: RootLevelFlatteningSheetGenerator

    @BeforeEach
    internal fun createGenerator() {
        this.sheetGenerator = RootLevelFlatteningSheetGenerator(SCHEMA)
    }

    @Test
    internal fun testGetHeaderRow() {
        assertLinesMatch(
            listOf(
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
                "A",
                "B",
                "C",
                "a",
                "b",
                "c",
            ),
            sheetGenerator.getHeaderRow(),
        )
    }

    @Test
    internal fun testGetRecordColumns() {
        val json = MAPPER.createObjectNode()
        // Field c is missing
        json.put("C", 3)
        json.put("B", "value B")
        json.set<JsonNode>("A", MAPPER.createObjectNode().put("Field 41", 15))
        json.put("b", "value b")
        json.put("a", 1)

        assertLinesMatch(
            // A, B, C, a, b, c
            listOf("{\"Field 41\":15}", "value B", "3", "1", "value b", ""),
            sheetGenerator.getRecordColumns(json),
        )
    }

    companion object {
        private val MAPPER: ObjectMapper = MoreMappers.initMapper()
        private val SCHEMA: ObjectNode = MAPPER.createObjectNode()

        init {
            val fields: List<String> = listOf("C", "B", "A", "c", "b", "a").shuffled()

            val schemaProperties = MAPPER.createObjectNode()
            for (field in fields) {
                schemaProperties.set<JsonNode>(field, MAPPER.createObjectNode())
            }

            SCHEMA.set<JsonNode>("properties", schemaProperties)
        }
    }
}
