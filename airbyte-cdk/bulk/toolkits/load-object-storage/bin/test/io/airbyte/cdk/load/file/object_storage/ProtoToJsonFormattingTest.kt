/*
 * Copyright (c) 2025 Airbyte, Inc.
 */
package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.mockk.every
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import java.io.ByteArrayOutputStream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ProtoToJsonFormattingTest : ProtoFixtures(true) {

    @Test
    fun `formatter writes ND-JSON with trailing newline`() {
        val out = ByteArrayOutputStream()
        val formatter = ProtoToJsonFormatter(stream, out, rootLevelFlattening = true)

        formatter.accept(record)
        formatter.flush()

        val lines = out.toString(Charsets.UTF_8).split('\n')
        assertEquals(2, lines.size) // record + final newline

        val expectedJson =
            """
            {"_airbyte_raw_id":"11111111-1111-1111-1111-111111111111","_airbyte_extracted_at":1724438400000,"_airbyte_meta":{"sync_id":42,"changes":[{"field":"x","change":"NULLED","reason":"DESTINATION_SERIALIZATION_ERROR"},{"field":"y","change":"NULLED","reason":"SOURCE_SERIALIZATION_ERROR"},{"field":"z","change":"TRUNCATED","reason":"SOURCE_RECORD_SIZE_LIMITATION"},{"field":"unknown_col","change":"NULLED","reason":"DESTINATION_SERIALIZATION_ERROR"}]},"_airbyte_generation_id":314,"bool_col":true,"int_col":123,"num_col":12.34,"string_col":"hello","date_col":"2025-06-17","time_tz_col":"23:59:59+02:00","time_no_tz_col":"23:59:59","ts_tz_col":"2025-06-17T23:59:59+02:00","ts_no_tz_col":"2025-06-17T23:59:59","array_col":["a","b"],"obj_col":{"k":"v"},"union_col":{"u":1},"unknown_col":null}
        """.trimIndent()

        assertEquals(
            expectedJson,
            lines[0],
        )
        assertEquals("", lines[1])
    }

    @Test
    fun `formatter writes ND-JSON with trailing newline non-flatten`() {
        val out = ByteArrayOutputStream()
        val formatter = ProtoToJsonFormatter(stream, out, rootLevelFlattening = false)

        formatter.accept(record)
        formatter.flush()

        val lines = out.toString(Charsets.UTF_8).split('\n')
        assertEquals(2, lines.size) // record + final newline

        val expectedJson =
            """
            {"_airbyte_raw_id":"11111111-1111-1111-1111-111111111111","_airbyte_extracted_at":1724438400000,"_airbyte_meta":{"sync_id":42,"changes":[{"field":"x","change":"NULLED","reason":"DESTINATION_SERIALIZATION_ERROR"},{"field":"y","change":"NULLED","reason":"SOURCE_SERIALIZATION_ERROR"},{"field":"z","change":"TRUNCATED","reason":"SOURCE_RECORD_SIZE_LIMITATION"},{"field":"unknown_col","change":"NULLED","reason":"DESTINATION_SERIALIZATION_ERROR"}]},"_airbyte_generation_id":314,"_airbyte_data":{"bool_col":true,"int_col":123,"num_col":12.34,"string_col":"hello","date_col":"2025-06-17","time_tz_col":"23:59:59+02:00","time_no_tz_col":"23:59:59","ts_tz_col":"2025-06-17T23:59:59+02:00","ts_no_tz_col":"2025-06-17T23:59:59","array_col":["a","b"],"obj_col":{"k":"v"},"union_col":{"u":1},"unknown_col":null}}
        """.trimIndent()

        assertEquals(
            expectedJson,
            lines[0],
        )
        assertEquals("", lines[1])
    }

    @Test
    fun `formatter throws on non-protobuf record`() {
        val nonProtoRecord =
            mockk<DestinationRecordRaw> {
                every { rawData } returns mockk<DestinationRecordSource>(relaxed = true)
            }
        val formatter = ProtoToJsonFormatter(stream, ByteArrayOutputStream(), false)

        val ex = assertThrows(RuntimeException::class.java) { formatter.accept(nonProtoRecord) }
        assertTrue(ex.message!!.contains("only supports conversion"))
    }
}
