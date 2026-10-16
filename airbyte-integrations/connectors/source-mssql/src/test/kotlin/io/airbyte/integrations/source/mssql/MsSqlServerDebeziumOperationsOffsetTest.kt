/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class MsSqlServerDebeziumOperationsOffsetTest {

    private val operations = debeziumOperationsWithoutDatabase()

    @Test
    fun `heartbeat offset with textual NULL change_lsn is normalized`() {
        assertNormalized("""{"commit_lsn":"$COMMIT","change_lsn":"NULL","event_serial_no":0}""")
    }

    @Test
    fun `heartbeat offset with JSON null change_lsn is normalized`() {
        assertNormalized("""{"commit_lsn":"$COMMIT","change_lsn":null,"event_serial_no":0}""")
    }

    @Test
    fun `Debezium snapshot offset is normalized`() {
        // Debezium 3.4.3 writes change_lsn = "NULL" in snapshot offsets too.
        assertNormalized(
            """{"snapshot":"INITIAL","snapshot_completed":true,"commit_lsn":"$COMMIT","change_lsn":"NULL","event_serial_no":1}"""
        )
    }

    @Test
    fun `offset with a real change_lsn is unchanged`() {
        assertUnchanged(
            """{"commit_lsn":"$COMMIT","change_lsn":"00033e76:0000cd58:0003","event_serial_no":2}"""
        )
    }

    @Test
    fun `cold start offset without change_lsn is unchanged`() {
        // Shape built by generateColdStartOffset().
        assertUnchanged("""{"commit_lsn":"$COMMIT","snapshot":true,"snapshot_completed":true}""")
    }

    @Test
    fun `serializeState writes the normalized offset`() {
        val serialized =
            operations.serializeState(
                offset("""{"commit_lsn":"$COMMIT","change_lsn":"NULL","event_serial_no":0}"""),
                null,
            )

        val encodedOffset =
            serialized[MsSqlServerDebeziumOperations.MSSQL_STATE][
                    MsSqlServerDebeziumOperations.MSSQL_CDC_OFFSET]
                .elements()
                .next()
        assertEquals(COMMIT, Jsons.readTree(encodedOffset.asText())["change_lsn"].asText())
    }

    /** Asserts only change_lsn changes, to commit_lsn, and the input is not mutated. */
    private fun assertNormalized(value: String) {
        val input = offset(value)
        val expected = Jsons.readTree(value) as ObjectNode
        expected.put("change_lsn", expected["commit_lsn"].asText())

        val normalized = operations.normalizeHeartbeatChangeLsn(input)

        assertEquals(mapOf(KEY to expected), normalized.wrapped)
        assertEquals(offset(value).wrapped, input.wrapped)
    }

    /** Asserts the offset comes back equal to the input, and the input is not mutated. */
    private fun assertUnchanged(value: String) {
        val input = offset(value)

        val normalized = operations.normalizeHeartbeatChangeLsn(input)

        assertEquals(offset(value).wrapped, normalized.wrapped)
        assertEquals(offset(value).wrapped, input.wrapped)
    }

    private fun offset(value: String) = DebeziumOffset(mapOf(KEY to Jsons.readTree(value)))

    companion object {
        private const val COMMIT = "00033e76:0000cd58:0008"
        private val KEY =
            Jsons.readTree("""["CdcTest",{"server":"CdcTest","database":"CdcTest"}]""")
    }
}
