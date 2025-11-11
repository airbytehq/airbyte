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
class ProtoToCsvFormattingTest : ProtoFixtures(true) {

    @Test
    fun `formatter writes csv with trailing newline`() {
        val out = ByteArrayOutputStream()
        val formatter =
            ProtoToCsvFormatter(
                stream,
                out,
                rootLevelFlattening = true,
                extractedAtAsTimestampWithTimezone = false,
            )

        formatter.accept(record)
        formatter.flush()

        val lines = out.toString(Charsets.UTF_8).split('\n')
        assertEquals(3, lines.size) // header + record + final newline

        val expectedHeader =
            """
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            "_airbyte_meta",
            "_airbyte_generation_id",
            "bool_col",
            "int_col",
            "num_col",
            "string_col",
            "date_col",
            "time_tz_col",
            "time_no_tz_col",
            "ts_tz_col",
            "ts_no_tz_col",
            "array_col",
            "obj_col",
            "union_col",
            "unknown_col"
        """
                .trimIndent()
                .replace("\n", "")
        assertEquals(
            expectedHeader,
            lines[0].trim(),
        )

        val expectedRecord =
            """
            "11111111-1111-1111-1111-111111111111",
            1724438400000,
            "{""sync_id"":42,""changes"":[{""field"":""x"",""change"":""NULLED"",""reason"":""DESTINATION_SERIALIZATION_ERROR""},{""field"":""y"",""change"":""NULLED"",""reason"":""SOURCE_SERIALIZATION_ERROR""},{""field"":""z"",""change"":""TRUNCATED"",""reason"":""SOURCE_RECORD_SIZE_LIMITATION""},{""field"":""unknown_col"",""change"":""NULLED"",""reason"":""DESTINATION_SERIALIZATION_ERROR""}]}",
            314,
            "true",
            123,
            12.34,
            "hello",
            "2025-06-17",
            "23:59:59+02:00",
            "23:59:59",
            "2025-06-17T23:59:59+02:00",
            "2025-06-17T23:59:59",
            "[""a"",""b""]",
            "{""k"":""v""}",
            "{""u"":1}",
            ""
        """
                .trimIndent()
                .replace("\n", "")

        assertEquals(
            expectedRecord,
            lines[1].trim(),
        )
        assertEquals("", lines[2].trim())
    }

    @Test
    fun `formatter writes csv with trailing newline non-flatten`() {
        val out = ByteArrayOutputStream()
        val formatter =
            ProtoToCsvFormatter(
                stream,
                out,
                rootLevelFlattening = false,
                extractedAtAsTimestampWithTimezone = false,
            )

        formatter.accept(record)
        formatter.flush()

        val lines = out.toString(Charsets.UTF_8).split('\n')
        assertEquals(3, lines.size) // header + record + final newline

        val expectedHeader =
            """
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            "_airbyte_meta",
            "_airbyte_generation_id",
            "_airbyte_data"
        """
                .trimIndent()
                .replace("\n", "")

        assertEquals(
            expectedHeader,
            lines[0].trim(),
        )

        val expectedRecord =
            """
            "11111111-1111-1111-1111-111111111111",
            1724438400000,
            "{""sync_id"":42,""changes"":[{""field"":""x"",""change"":""NULLED"",""reason"":""DESTINATION_SERIALIZATION_ERROR""},{""field"":""y"",""change"":""NULLED"",""reason"":""SOURCE_SERIALIZATION_ERROR""},{""field"":""z"",""change"":""TRUNCATED"",""reason"":""SOURCE_RECORD_SIZE_LIMITATION""},{""field"":""unknown_col"",""change"":""NULLED"",""reason"":""DESTINATION_SERIALIZATION_ERROR""}]}",
            314,
            "{""bool_col"":true,""int_col"":123,""num_col"":12.34,""string_col"":""hello"",""date_col"":""2025-06-17"",""time_tz_col"":""23:59:59+02:00"",""time_no_tz_col"":""23:59:59"",""ts_tz_col"":""2025-06-17T23:59:59+02:00"",""ts_no_tz_col"":""2025-06-17T23:59:59"",""array_col"":[""a"",""b""],""obj_col"":{""k"":""v""},""union_col"":{""u"":1},""unknown_col"":null}"
        """
                .trimIndent()
                .replace("\n", "")

        assertEquals(
            expectedRecord,
            lines[1].trim(),
        )
        assertEquals("", lines[2].trim())
    }

    @Test
    fun `formatter throws on non-protobuf record`() {
        val nonProtoRecord =
            mockk<DestinationRecordRaw> {
                every { rawData } returns mockk<DestinationRecordSource>(relaxed = true)
            }
        val formatter = ProtoToCsvFormatter(stream, ByteArrayOutputStream(), false, false)

        val ex = assertThrows(RuntimeException::class.java) { formatter.accept(nonProtoRecord) }
        assertTrue(
            ex.message!!.contains(
                "ProtoToCsvFormatter only supports DestinationRecordProtobufSource",
            ),
        )
    }
}
