/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.assertNoErrors
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.configured
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.discover
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.execute
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.ids
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.lastStateOf
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.read
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.recordsOf
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.statesOf
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.streamState
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

/**
 * Cold sync, mutation, warm sync and a second warm sync for every cursor-able type. Rows equal to
 * the saved cursor are re-emitted (at-least-once); rows below it must not appear. Nanosecond
 * cursors are rounded up to microseconds, so a row between the true max and the rounded state value
 * is not re-emitted (`INC_TS_*` row 3).
 */
class SnowflakeSourceCursorIncrementalLiveTest : AbstractSnowflakeLiveTest() {

    data class CursorCase(
        val table: String,
        /** JSON literal of the cursor value in the state after the cold sync. */
        val coldMax: String,
        /** Rows 4 (below), 5 (equal) and 6 (above) inserted after the cold sync. */
        val mutation: String,
        /** IDs the warm sync must emit. */
        val warmIds: List<Long>,
        /** JSON literal of the cursor value in the state after the warm sync. */
        val warmMax: String,
        /**
         * IDs a third sync from the warm state emits: normally the row equal to the saved cursor. A
         * nanosecond cursor is saved rounded up to microseconds, so a row whose value lies between
         * the true max and the rounded state is not re-emitted (no loss: it was emitted before).
         */
        val warmAgainIds: List<Long> = listOf(6),
    ) {
        override fun toString(): String = table
    }

    private lateinit var catalog: AirbyteCatalog

    @BeforeAll
    fun discoverOnce() {
        catalog = discover(spec())
    }

    fun cases(): List<CursorCase> =
        listOf(
            CursorCase(
                "INC_NUMBER",
                "12345678901234567.1234567891",
                "VALUES (4, 5.5, 'below'), (5, 12345678901234567.1234567891, 'equal'), (6, 12345678901234567.1234567892, 'above')",
                listOf(3, 5, 6),
                "12345678901234567.1234567892",
            ),
            CursorCase(
                "INC_TS_NTZ",
                "\"2026-01-02T04:00:00.000001\"",
                "SELECT 4, '2026-01-02 03:00:00'::TIMESTAMP_NTZ(9), 'below' UNION ALL SELECT 5, '2026-01-02 04:00:00.000001'::TIMESTAMP_NTZ(9), 'equal' UNION ALL SELECT 6, '2026-01-02 05:00:00.000000001'::TIMESTAMP_NTZ(9), 'above'",
                listOf(5, 6),
                "\"2026-01-02T05:00:00.000001\"",
                warmAgainIds = emptyList(),
            ),
            CursorCase(
                "INC_TS_TZ",
                "\"2026-01-02T12:00:00.000001Z\"",
                "SELECT 4, '2026-01-02 03:00:00 -08:00'::TIMESTAMP_TZ(9), 'below' UNION ALL SELECT 5, '2026-01-02 17:30:00.000001 +05:30'::TIMESTAMP_TZ(9), 'equal' UNION ALL SELECT 6, '2026-01-02 05:00:00 -08:00'::TIMESTAMP_TZ(9), 'above'",
                listOf(5, 6),
                "\"2026-01-02T13:00:00.000000Z\"",
            ),
            CursorCase(
                "INC_TS_LTZ",
                "\"2026-01-02T12:00:00.000001Z\"",
                "SELECT 4, '2026-01-02 11:00:00 +00:00'::TIMESTAMP_LTZ(9), 'below' UNION ALL SELECT 5, '2026-01-02 12:00:00.000001 +00:00'::TIMESTAMP_LTZ(9), 'equal' UNION ALL SELECT 6, '2026-01-02 13:00:00 +00:00'::TIMESTAMP_LTZ(9), 'above'",
                listOf(5, 6),
                "\"2026-01-02T13:00:00.000000Z\"",
            ),
            CursorCase(
                "INC_DATE",
                "\"2026-01-03\"",
                "VALUES (4, '2026-01-02', 'below'), (5, '2026-01-03', 'equal'), (6, '2026-01-04', 'above')",
                listOf(3, 5, 6),
                "\"2026-01-04\"",
            ),
            CursorCase(
                "INC_VARCHAR",
                "\"c\"",
                "VALUES (4, 'b', 'below'), (5, 'c', 'equal'), (6, 'd', 'above')",
                listOf(3, 5, 6),
                "\"d\"",
            ),
            CursorCase(
                "INC_NOPK_NUMBER",
                "30",
                "VALUES (4, 25, 'below'), (5, 30, 'equal'), (6, 40, 'above')",
                listOf(3, 5, 6),
                "40",
            ),
        )

    private fun cursorState(cursor: String): JsonNode =
        Jsons.readTree("""{"primary_key":{},"cursors":{"CUR":$cursor}}""")

    private fun incremental(table: String): ConfiguredAirbyteCatalog =
        configured(catalog, listOf(table), SyncMode.INCREMENTAL, cursor = "CUR")

    @ParameterizedTest
    @MethodSource("cases")
    fun coldThenWarmThenWarmAgain(case: CursorCase) {
        val cold = read(spec(), incremental(case.table))
        cold.assertNoErrors()
        assertEquals(listOf<Long>(1, 2, 3), ids(cold.recordsOf(case.table)))
        val coldState = cold.lastStateOf(case.table)
        assertNotNull(coldState)
        assertEquals(cursorState(case.coldMax), coldState)

        execute(admin, "INSERT INTO \"$database\".\"$schema\".\"${case.table}\" ${case.mutation}")

        val warm =
            read(
                spec(),
                incremental(case.table),
                listOf(streamState(case.table, schema, coldState.toString()))
            )
        warm.assertNoErrors()
        assertEquals(case.warmIds, ids(warm.recordsOf(case.table)))
        val warmState = warm.lastStateOf(case.table)
        assertEquals(cursorState(case.warmMax), warmState)

        // Nothing new: only the row equal to the saved cursor comes back, the state stays.
        val again =
            read(
                spec(),
                incremental(case.table),
                listOf(streamState(case.table, schema, warmState.toString()))
            )
        again.assertNoErrors()
        assertEquals(case.warmAgainIds, ids(again.recordsOf(case.table)))
        assertEquals(warmState, again.lastStateOf(case.table))
    }

    @Test
    fun emptyIncrementalTableEmitsNothing() {
        val out =
            read(
                spec(),
                configured(catalog, listOf("EMPTY_TABLE"), SyncMode.INCREMENTAL, cursor = "ID")
            )
        out.assertNoErrors()
        assertEquals(0, out.recordsOf("EMPTY_TABLE").size)
        assertEquals(0, out.statesOf("EMPTY_TABLE").size)
    }

    @Test
    @Disabled(
        "airbytehq/airbyte#83800: with the account default TIMEZONE (America/Los_Angeles) the NTZ " +
            "cursor bound is shifted by the session offset and the warm sync misses rows; 0 of 1 new " +
            "rows were read on 2.0.1. Enable once the fix is merged."
    )
    fun ntzCursorWithAccountDefaultSessionTimezone() {
        execute(
            admin,
            "CREATE TABLE \"$database\".\"$schema\".INC_TS_NTZ_DEFAULT_TZ LIKE \"$database\".\"$schema\".INC_TS_NTZ"
        )
        execute(
            admin,
            "INSERT INTO \"$database\".\"$schema\".INC_TS_NTZ_DEFAULT_TZ SELECT * FROM \"$database\".\"$schema\".INC_TS_NTZ WHERE ID <= 3"
        )
        val spec = spec(sessionTimezone = null)
        val catalogWithNewTable = discover(spec)
        val configured =
            configured(
                catalogWithNewTable,
                listOf("INC_TS_NTZ_DEFAULT_TZ"),
                SyncMode.INCREMENTAL,
                cursor = "CUR"
            )
        val cold = read(spec, configured)
        val coldState = cold.lastStateOf("INC_TS_NTZ_DEFAULT_TZ")!!
        execute(
            admin,
            "INSERT INTO \"$database\".\"$schema\".INC_TS_NTZ_DEFAULT_TZ SELECT 6, '2026-01-02 05:00:00'::TIMESTAMP_NTZ(9), 'above'"
        )
        val warm =
            read(
                spec,
                configured,
                listOf(streamState("INC_TS_NTZ_DEFAULT_TZ", schema, coldState.toString()))
            )
        assertEquals(listOf<Long>(6), ids(warm.recordsOf("INC_TS_NTZ_DEFAULT_TZ")))
    }
}
