/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.util.Jsons
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class MsSqlServerDebeziumOperationsOffsetTest {

    private val operations = operations()

    @ParameterizedTest(name = "{0}")
    @MethodSource("normalizedCases")
    fun `normalizeHeartbeatChangeLsn sets change_lsn to commit_lsn`(
        @Suppress("UNUSED_PARAMETER") name: String,
        value: String,
    ) {
        val input = offset(value)
        val expected = Jsons.readTree(value) as ObjectNode
        expected.put("change_lsn", expected["commit_lsn"].asText())

        val normalized = operations.normalizeHeartbeatChangeLsn(input)

        assertEquals(mapOf(KEY to expected), normalized.wrapped)
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("unchangedCases")
    fun `normalizeHeartbeatChangeLsn leaves offset untouched`(
        @Suppress("UNUSED_PARAMETER") name: String,
        values: List<String>,
    ) {
        val input = offset(*values.toTypedArray())
        assertSame(input.wrapped, operations.normalizeHeartbeatChangeLsn(input).wrapped)
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

    companion object {
        private const val COMMIT = "00033e76:0000cd58:0008"
        private val KEY =
            Jsons.readTree("""["CdcTest",{"server":"CdcTest","database":"CdcTest"}]""")

        private fun offset(vararg values: String): DebeziumOffset =
            DebeziumOffset(
                values
                    .mapIndexed { i, v ->
                        val key = if (i == 0) KEY else Jsons.readTree("""["CdcTest$i"]""")
                        key to Jsons.readTree(v)
                    }
                    .toMap()
            )

        @JvmStatic
        fun normalizedCases(): List<Arguments> =
            listOf(
                Arguments.of(
                    "heartbeat with textual NULL",
                    """{"commit_lsn":"$COMMIT","change_lsn":"NULL","event_serial_no":0}""",
                ),
                Arguments.of(
                    "heartbeat with JSON null",
                    """{"commit_lsn":"$COMMIT","change_lsn":null,"event_serial_no":0}""",
                ),
                // Debezium 3.4.3 always writes change_lsn, including for snapshot offsets.
                Arguments.of(
                    "Debezium snapshot offset",
                    """{"snapshot":"INITIAL","snapshot_completed":true,"commit_lsn":"$COMMIT","change_lsn":"NULL","event_serial_no":1}""",
                ),
            )

        @JvmStatic
        fun unchangedCases(): List<Arguments> =
            listOf(
                Arguments.of(
                    "real change_lsn",
                    listOf(
                        """{"commit_lsn":"$COMMIT","change_lsn":"00033e76:0000cd58:0003","event_serial_no":2}"""
                    ),
                ),
                // Shape built by generateColdStartOffset().
                Arguments.of(
                    "cold start offset without change_lsn",
                    listOf(
                        """{"commit_lsn":"$COMMIT","snapshot":true,"snapshot_completed":true}"""
                    ),
                ),
                Arguments.of(
                    "NULL commit_lsn",
                    listOf("""{"commit_lsn":"NULL","change_lsn":"NULL","event_serial_no":0}"""),
                ),
                Arguments.of(
                    "multiple offset keys",
                    listOf(
                        """{"commit_lsn":"$COMMIT","change_lsn":"NULL"}""",
                        """{"commit_lsn":"$COMMIT","change_lsn":null}""",
                    ),
                ),
            )

        private fun operations(): MsSqlServerDebeziumOperations {
            val spec =
                MsSqlServerSourceConfigurationSpecification().apply {
                    host = "localhost"
                    port = 1433
                    database = "CdcTest"
                    username = "sa"
                    password = "Password123!"
                    setIncrementalValue(Cdc())
                }
            val config = MsSqlServerSourceConfigurationFactory().make(spec)
            return MsSqlServerDebeziumOperations(
                mockk<JdbcConnectionFactory>(relaxed = true),
                config
            )
        }
    }
}
