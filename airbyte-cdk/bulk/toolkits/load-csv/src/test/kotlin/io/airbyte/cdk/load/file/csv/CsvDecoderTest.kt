/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.csv

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

const val CSV_CONTENT: String = """
id,value
ID_0,value_0
ID_1,value_1
"""

class CsvDecoderTest {

    private lateinit var decoder: CsvDecoder

    @BeforeEach
    fun setup() {
        decoder = CsvDecoder()
    }

    @Test
    internal fun `test given valid cdk when decode then return each row`() {
        val csvEntries = decoder.decode(CSV_CONTENT.byteInputStream()).use { it.toList() }

        Assertions.assertEquals(2, csvEntries.size)
        Assertions.assertEquals(csvEntries[0], recordAtIndex(0))
        Assertions.assertEquals(csvEntries[1], recordAtIndex(1))
    }

    private fun recordAtIndex(index: Int): JsonNode {
        return Jsons.readTree("""
{
    "id": "ID_${index}",
    "value": "value_${index}"
}
""")
    }
}
