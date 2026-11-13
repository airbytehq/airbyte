/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.spec

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class LoadFormatSpecTest {

    @Test
    fun `csv format is not json and carries no compression`() {
        val csv: LoadFormatSpec = CsvFormat()
        assertFalse(csv.isJson)
        assertEquals(LoadCompression.NONE, csv.compression)
    }

    @Test
    fun `json format is json and exposes its compression`() {
        assertTrue(JsonFormat().isJson)
        assertEquals(LoadCompression.NONE, JsonFormat().compression)
        assertEquals(LoadCompression.GZIP, JsonFormat("gzip").compression)
        assertEquals(LoadCompression.ZSTD, JsonFormat("zstd").compression)
    }

    @Test
    fun `deserializes the oneOf branches by the format_type discriminator`() {
        val mapper = jacksonObjectMapper()

        val csv = mapper.readValue("""{"format_type":"CSV"}""", LoadFormatSpec::class.java)
        assertInstanceOf(CsvFormat::class.java, csv)

        val json =
            mapper.readValue(
                """{"format_type":"JSON","compression":"zstd"}""",
                LoadFormatSpec::class.java
            )
        assertInstanceOf(JsonFormat::class.java, json)
        assertEquals("zstd", (json as JsonFormat).compression)

        // JSON branch with compression omitted falls back to "none".
        val jsonDefault = mapper.readValue("""{"format_type":"JSON"}""", LoadFormatSpec::class.java)
        assertEquals(LoadCompression.NONE, (jsonDefault as JsonFormat).compression)
    }
}
