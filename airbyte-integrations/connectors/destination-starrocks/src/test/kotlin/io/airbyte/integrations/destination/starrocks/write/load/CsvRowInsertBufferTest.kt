/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.integrations.destination.starrocks.http.StreamLoadClient
import java.math.BigInteger
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Pure unit tests for the CSV buffer + `__op` mapping. No live StarRocks: we never call [flush]
 * (which issues HTTP), only [CsvRowInsertBuffer.accumulate] / [CsvRowInsertBuffer.columnsHeader].
 */
class CsvRowInsertBufferTest {

    // Never used because flush() is not exercised; a placeholder so the buffer can be constructed.
    private val unusedClient = StreamLoadClient("localhost", 8030, "u", "p")
    private val table = TableName("db", "orders")
    private val columns = listOf("_airbyte_raw_id", "id", "name", CDC_DELETED_AT_COLUMN)

    private fun buffer(cdc: Boolean) =
        CsvRowInsertBuffer(table, columns, cdcDeleteEnabled = cdc, streamLoadClient = unusedClient)

    @Test
    fun `cdc delete row appends __op=1 when deleted_at is present`() {
        val buf = buffer(cdc = true)
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-1"),
                "id" to IntegerValue(BigInteger.valueOf(7)),
                "name" to StringValue("alice"),
                CDC_DELETED_AT_COLUMN to StringValue("2026-01-01T00:00:00Z"),
            ),
        )

        val row = buf.csvSnapshot().trimEnd('\n')
        assertTrue(row.endsWith(",1"), "deleted row must end with __op=1, got: $row")
        assertEquals("\"rid-1\",7,\"alice\",\"2026-01-01T00:00:00Z\",1", row)
    }

    @Test
    fun `cdc upsert row appends __op=0 when deleted_at is null or absent`() {
        val buf = buffer(cdc = true)
        // _ab_cdc_deleted_at explicitly NullValue
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-2"),
                "id" to IntegerValue(BigInteger.valueOf(8)),
                "name" to StringValue("bob"),
                CDC_DELETED_AT_COLUMN to NullValue,
            ),
        )
        // _ab_cdc_deleted_at key absent entirely
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-3"),
                "id" to IntegerValue(BigInteger.valueOf(9)),
                "name" to StringValue("carol"),
            ),
        )

        val rows = buf.csvSnapshot().trim('\n').split("\n")
        assertEquals(2, rows.size)
        // NullValue cell renders as \N, and __op=0
        assertEquals("\"rid-2\",8,\"bob\",\\N,0", rows[0])
        assertEquals("\"rid-3\",9,\"carol\",\\N,0", rows[1])
    }

    @Test
    fun `non-cdc row has no __op cell`() {
        val buf = buffer(cdc = false)
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-4"),
                "id" to IntegerValue(BigInteger.valueOf(1)),
                "name" to StringValue("dan"),
            ),
        )
        val row = buf.csvSnapshot().trimEnd('\n')
        // 4 columns, no trailing __op
        assertEquals("\"rid-4\",1,\"dan\",\\N", row)
        assertFalse(row.endsWith(",0") || row.endsWith(",1"), "non-cdc row must not carry __op")
    }

    @Test
    fun `soft delete upserts (__op=0) even when deleted_at is present, retaining the tombstone`() {
        val buf =
            CsvRowInsertBuffer(
                table,
                columns,
                cdcDeleteEnabled = true,
                streamLoadClient = unusedClient,
                softDelete = true,
            )
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-9"),
                "id" to IntegerValue(BigInteger.valueOf(42)),
                "name" to StringValue("erin"),
                CDC_DELETED_AT_COLUMN to StringValue("2026-01-01T00:00:00Z"),
            ),
        )
        val row = buf.csvSnapshot().trimEnd('\n')
        // Hard delete would emit __op=1 and drop the row; soft delete keeps it via __op=0.
        assertEquals("\"rid-9\",42,\"erin\",\"2026-01-01T00:00:00Z\",0", row)
        assertTrue(row.endsWith(",0"), "soft-deleted row must upsert (__op=0), got: $row")
    }

    @Test
    fun `timestamps render as StarRocks DATETIME — space separated, no T or Z, tz normalized to UTC`() {
        val buf = buffer(cdc = false)
        // tz-aware 2026-06-24T10:53:44+09:00 -> UTC 01:53:44
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-tz"),
                "id" to IntegerValue(BigInteger.ONE),
                "name" to
                    TimestampWithTimezoneValue(
                        OffsetDateTime.of(2026, 6, 24, 10, 53, 44, 0, ZoneOffset.ofHours(9)),
                    ),
            ),
        )
        // tz-naive stays as-is, just reformatted
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-naive"),
                "id" to IntegerValue(BigInteger.TWO),
                "name" to TimestampWithoutTimezoneValue(LocalDateTime.of(2026, 6, 24, 8, 0, 1)),
            ),
        )
        val rows = buf.csvSnapshot().trim('\n').split("\n")
        assertEquals("\"rid-tz\",1,2026-06-24 01:53:44,\\N", rows[0])
        assertEquals("\"rid-naive\",2,2026-06-24 08:00:01,\\N", rows[1])
    }

    @Test
    fun `streamLoadLabel is stable for identical content and differs for different content`() {
        val buf = buffer(cdc = false)
        val a = "\"rid-a\",1\n".toByteArray()
        val b = "\"rid-b\",2\n".toByteArray()
        // Same batch retried -> same label (StarRocks dedups via "Label Already Exists").
        assertEquals(buf.streamLoadLabel(a), buf.streamLoadLabel(a))
        // Different batch -> different label (no accidental dedup of distinct data).
        assertNotEquals(buf.streamLoadLabel(a), buf.streamLoadLabel(b))
        // Label must be safe to send as an HTTP header value.
        assertTrue(buf.streamLoadLabel(a).none { it.isWhitespace() || it.isISOControl() })
    }

    @Test
    fun `strings are quoted and internal quotes are doubled`() {
        val buf = buffer(cdc = false)
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-5"),
                "id" to IntegerValue(BigInteger.ONE),
                "name" to StringValue("""she said "hi", ok"""),
            ),
        )
        val row = buf.csvSnapshot().trimEnd('\n')
        // embedded quotes doubled; the comma inside the quoted field is preserved
        assertTrue(row.contains("\"she said \"\"hi\"\", ok\""), "quotes must be escaped, got: $row")
    }

    @Test
    fun `object value is serialized to json and quoted`() {
        val buf = buffer(cdc = false)
        val obj = ObjectValue(linkedMapOf("k" to StringValue("v")))
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-6"),
                "id" to IntegerValue(BigInteger.ZERO),
                "name" to obj,
            ),
        )
        val row = buf.csvSnapshot().trimEnd('\n')
        // {"k":"v"} serialized then enclosed; internal quotes doubled
        assertTrue(
            row.contains("\"{\"\"k\"\":\"\"v\"\"}\""),
            "object must be json+quoted, got: $row"
        )
    }

    @Test
    fun `columns header includes __op only for dedup cdc`() {
        assertEquals(
            "_airbyte_raw_id,id,name,$CDC_DELETED_AT_COLUMN,__op",
            buffer(cdc = true).columnsHeader(),
        )
        assertEquals(
            "_airbyte_raw_id,id,name,$CDC_DELETED_AT_COLUMN",
            buffer(cdc = false).columnsHeader(),
        )
    }

    @Test
    fun `boolean renders as 1 or 0`() {
        val buf = buffer(cdc = false)
        buf.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid-7"),
                "id" to IntegerValue(BigInteger.TEN),
                "name" to BooleanValue(true),
            ),
        )
        val row = buf.csvSnapshot().trimEnd('\n')
        assertEquals("\"rid-7\",10,1,\\N", row)
    }

    @Test
    fun `stream load headers contain no control characters`() {
        // Regression: a raw "\n" in the row_delimiter header made OkHttp reject the request
        // ("Unexpected char 0x0a"). Every header VALUE must be free of control chars.
        for ((k, v) in buffer(cdc = true).streamLoadHeaders()) {
            assertTrue(v.all { it.code >= 0x20 }, "header '$k' must not contain a control char: $v")
        }
    }

    @Test
    fun `stream load headers omit row_delimiter and escape`() {
        val h = buffer(cdc = false).streamLoadHeaders()
        assertEquals("CSV", h["format"])
        assertEquals(",", h["column_separator"])
        assertEquals("\"", h["enclose"])
        assertTrue(h.containsKey("columns"))
        // row_delimiter (raw \n) and escape (collides with \N null) are intentionally not sent.
        assertFalse(h.containsKey("row_delimiter"))
        assertFalse(h.containsKey("escape"))
    }
}
