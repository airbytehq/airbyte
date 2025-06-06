package io.airbyte.cdk.load.http.decoder

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.util.Jsons
import java.io.InputStream
import java.io.InputStreamReader
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

val CSV_CONTENT: String = """
id,value
ID_0,value_0
ID_1,value_1
"""

val FIRST_RECORD: String = """
{
    "id": "ID_1",
    "value": "value_1"
""".trimIndent()

class CsvDecoderTest {

    private lateinit var decoder: CsvDecoder

    @BeforeEach
    fun setup() {
        decoder = CsvDecoder()
    }

    @Test
    internal fun `test given valid cdk when decode then return each row`() {
        val csvEntries = decoder.decode(Response(200, mapOf(), CSV_CONTENT.byteInputStream())).use{ it.toList() }

        Assertions.assertEquals(2, csvEntries.size)
        Assertions.assertEquals(csvEntries[0], recordAtIndex(0))
        Assertions.assertEquals(csvEntries[1], recordAtIndex(1))
    }

    @Test
    internal fun `test when decode then close input stream`() {
        val inputStream = CSV_CONTENT.byteInputStream()
        val csvEntries = decoder.decode(Response(200, mapOf(), inputStream)).use{ it.toList() }

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
