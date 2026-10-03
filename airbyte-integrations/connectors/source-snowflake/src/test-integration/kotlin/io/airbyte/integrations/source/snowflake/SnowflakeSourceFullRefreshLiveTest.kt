/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.assertNoErrors
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.configured
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.discover
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.ids
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.lastStateOf
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.read
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.recordsOf
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.statesOf
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.streamState
import io.airbyte.protocol.models.v0.AirbyteCatalog
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class SnowflakeSourceFullRefreshLiveTest : AbstractSnowflakeLiveTest() {

    private lateinit var catalog: AirbyteCatalog
    private val completeState: JsonNode = Jsons.readTree("""{"primary_key":{},"cursors":{}}""")

    @BeforeAll
    fun discoverOnce() {
        catalog = discover(spec())
    }

    @Test
    fun typeMatrixValues() {
        val out = read(spec(), configured(catalog, listOf("TYPE_MATRIX")))
        out.assertNoErrors()
        val rows = out.recordsOf("TYPE_MATRIX").associateBy { it["ID"].asInt() }
        assertEquals(setOf(1, 2), rows.keys)
        val r = rows[1]!!
        assertEquals("99999999999999999999999999999999999999", r["C_NUMBER"].asText())
        assertEquals("2147483648", r["C_INT"].asText())
        assertEquals("9223372036854775808", r["C_BIGINT"].asText())
        assertEquals("32768", r["C_SMALLINT"].asText())
        assertEquals("128", r["C_BYTEINT"].asText())
        assertEquals("12345678.91", r["C_NUMBER_10_2"].decimalValue().toPlainString())
        assertEquals(
            "1234567890123456789012345678.1234567890",
            r["C_NUMERIC"].decimalValue().toPlainString()
        )
        assertEquals(1.5, r["C_FLOAT"].asDouble())
        assertEquals("héllo wörld 日本語 🎉", r["C_VARCHAR"].asText())
        assertEquals("abc", r["C_CHAR"].asText())
        assertEquals("3q2+7w==", r["C_BINARY"].asText())
        assertTrue(r["C_BOOLEAN"].asBoolean())
        assertEquals("2026-03-08", r["C_DATE"].asText())
        // TIME was NULL for every row before 2.0.2 (driver rejects getObject(LocalTime)).
        assertEquals("13:14:15.123457", r["C_TIME"].asText())
        assertEquals("13:14:15.123000", r["C_TIME3"].asText())
        assertEquals("2026-03-08T01:59:59.123457", r["C_TIMESTAMP_NTZ"].asText())
        assertEquals("2026-03-08T09:59:59.123457Z", r["C_TIMESTAMP_LTZ"].asText())
        assertEquals("2026-03-08T09:59:59.123457Z", r["C_TIMESTAMP_TZ"].asText())
        assertTrue(r["C_VARIANT"].isTextual)
        assertTrue(r["C_GEOGRAPHY"].asText().contains("\"type\": \"Point\""))
        assertEquals("[1.1,2.2,3.3]", r["C_VECTOR"].asText())
        val nulls = rows[2]!!
        nulls
            .fieldNames()
            .asSequence()
            .filter { it != "ID" }
            .forEach { assertTrue(nulls[it].isNull, it) }
        assertEquals(completeState, out.lastStateOf("TYPE_MATRIX"))
    }

    @Test
    fun emptyTableEmitsOneCompleteState() {
        val out = read(spec(), configured(catalog, listOf("EMPTY_TABLE")))
        out.assertNoErrors()
        assertEquals(0, out.recordsOf("EMPTY_TABLE").size)
        assertEquals(listOf(completeState), out.statesOf("EMPTY_TABLE"))
    }

    @Test
    fun viewAndTableWithoutPrimaryKey() {
        val out = read(spec(), configured(catalog, listOf("V_TYPES", "NO_PK")))
        out.assertNoErrors()
        assertEquals(2, out.recordsOf("V_TYPES").size)
        assertEquals(5, out.recordsOf("NO_PK").size)
        assertEquals(completeState, out.lastStateOf("V_TYPES"))
        assertEquals(completeState, out.lastStateOf("NO_PK"))
    }

    @Test
    fun resumeFromPrimaryKeyCheckpoint() {
        val state = streamState("PK_TABLE", schema, """{"primary_key":{"ID":5},"cursors":{}}""")
        val out = read(spec(), configured(catalog, listOf("PK_TABLE")), listOf(state))
        out.assertNoErrors()
        assertEquals(listOf<Long>(6, 7, 8, 9, 10), ids(out.recordsOf("PK_TABLE")))
        assertEquals(completeState, out.lastStateOf("PK_TABLE"))
    }

    @Test
    fun resumeFromCompositePrimaryKeyCheckpoint() {
        val state =
            streamState("COMPOSITE_PK", schema, """{"primary_key":{"A":1,"B":"b"},"cursors":{}}""")
        val out = read(spec(), configured(catalog, listOf("COMPOSITE_PK")), listOf(state))
        out.assertNoErrors()
        val keys =
            out.recordsOf("COMPOSITE_PK")
                .map { it["A"].asInt() to it["B"].asText() }
                .sortedWith(compareBy({ it.first }, { it.second }))
        assertEquals(listOf(2 to "a", 2 to "b", 3 to "a"), keys)
    }

    @Test
    fun completedStateReadsNothing() {
        // CDK semantics for a resumable full refresh: the final state means "done"; the platform
        // clears it before the next full refresh.
        val out =
            read(
                spec(),
                configured(catalog, listOf("PK_TABLE")),
                listOf(streamState("PK_TABLE", schema, completeState.toString()))
            )
        out.assertNoErrors()
        assertEquals(0, out.recordsOf("PK_TABLE").size)
    }

    @Test
    fun concurrentChunksCoverTheTableExactlyOnce() {
        // target chunk size = 10 MB/s / 8 * 1 s = 1.25 MB, so ~100k rows of ~100 B are split.
        val out =
            read(
                spec(concurrency = 8, checkpointSeconds = 1),
                configured(catalog, listOf("SPLIT_100K"))
            )
        out.assertNoErrors()
        val allIds = ids(out.recordsOf("SPLIT_100K"))
        assertEquals(100_000, allIds.size)
        assertEquals(100_000, allIds.toSet().size)
        val states = out.statesOf("SPLIT_100K")
        assertTrue(states.size >= 3, "expected several chunk checkpoints, got ${states.size}")
        val bounds = states.dropLast(1).map { it["primary_key"]["ID"].asLong() }
        assertEquals(bounds.sorted(), bounds, "chunk checkpoints must be emitted in PK order")
        assertEquals(completeState, states.last())
    }
}
