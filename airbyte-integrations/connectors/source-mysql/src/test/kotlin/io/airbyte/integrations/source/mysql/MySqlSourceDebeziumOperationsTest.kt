/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.read.cdc.AbortDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ResetDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mysql.MySqlSourceDebeziumOperations.Companion.MYSQL_CDC_OFFSET
import io.airbyte.integrations.source.mysql.MySqlSourceDebeziumOperations.Companion.STATE
import io.airbyte.integrations.source.mysql.MySqlSourceDebeziumOperations.Companion.deserializeStateUnvalidated
import io.mockk.every
import io.mockk.mockk
import java.sql.Connection
import java.sql.ResultSet
import java.sql.ResultSetMetaData
import java.sql.Statement
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MySqlSourceDebeziumOperationsTest {

    /** Builds a minimal CDC state [ObjectNode] that [deserializeStateUnvalidated] can parse. */
    private fun buildStateNode(
        file: String = "mysql-bin.000001",
        pos: Long = 154,
        gtids: String? = null,
        gtidsExplicitNull: Boolean = false,
    ): ObjectNode {
        val offsetKey =
            Jsons.arrayNode().apply {
                add("testdb")
                add(Jsons.objectNode().apply { put("server", "testdb") })
            }
        val offsetValue =
            Jsons.objectNode().apply {
                put("ts_sec", 1234567890)
                put("file", file)
                put("pos", pos)
                if (gtidsExplicitNull) {
                    // Simulate Jackson NullNode.asText() == "null"
                    set<com.fasterxml.jackson.databind.JsonNode>(
                        "gtids",
                        com.fasterxml.jackson.databind.node.NullNode.getInstance()
                    )
                } else if (gtids != null) {
                    put("gtids", gtids)
                }
            }
        val offsetNode =
            Jsons.objectNode().apply {
                put(
                    Jsons.writeValueAsString(offsetKey),
                    Jsons.writeValueAsString(offsetValue),
                )
            }
        return Jsons.objectNode().apply {
            set<ObjectNode>(
                STATE,
                Jsons.objectNode().apply { set<ObjectNode>(MYSQL_CDC_OFFSET, offsetNode) }
            )
        }
    }

    // ──────────────── parseSavedOffset / deserializeStateUnvalidated tests ────────────────

    @Test
    fun `deserializeStateUnvalidated parses normal gtid set`() {
        val gtidValue = "3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5"
        val stateNode = buildStateNode(gtids = gtidValue)
        val result = deserializeStateUnvalidated(stateNode)
        val offsetValues = result.offset.wrapped.values.first() as ObjectNode
        assertEquals(gtidValue, offsetValues["gtids"]?.asText())
    }

    @Test
    fun `deserializeStateUnvalidated parses null gtid node`() {
        // When "gtids" is a JSON null (NullNode), asText() returns the literal "null" string.
        // The fix in parseSavedOffset should treat this as absent.
        val stateNode = buildStateNode(gtidsExplicitNull = true)
        val result = deserializeStateUnvalidated(stateNode)
        val offsetValues = result.offset.wrapped.values.first() as ObjectNode
        // The raw deserialized state still has the NullNode; the filtering is in parseSavedOffset.
        assertTrue(offsetValues.has("gtids"))
    }

    @Test
    fun `deserializeStateUnvalidated parses state without gtids field`() {
        val stateNode = buildStateNode()
        val result = deserializeStateUnvalidated(stateNode)
        val offsetValues = result.offset.wrapped.values.first() as ObjectNode
        assertNull(offsetValues["gtids"])
    }

    // ──────────── Integration tests: deserializeState with mocked JDBC ────────────

    /**
     * Creates a [MySqlSourceDebeziumOperations] with mocked JDBC that simulates a MySQL server with
     * the given binlog position and GTID set.
     */
    private fun createOpsWithMockedJdbc(
        serverFile: String = "mysql-bin.000001",
        serverPos: Long = 154,
        serverGtidSet: String? = null,
        behavior: InvalidCdcCursorPositionBehavior = InvalidCdcCursorPositionBehavior.FAIL_SYNC,
        binaryLogFiles: List<String> = listOf("mysql-bin.000001"),
    ): MySqlSourceDebeziumOperations {
        val rsMetaData = mockk<ResultSetMetaData>()
        every { rsMetaData.columnCount } returns if (serverGtidSet != null) 5 else 4

        val rs = mockk<ResultSet>()
        every { rs.next() } returns true
        every { rs.getString("File") } returns serverFile
        every { rs.wasNull() } returns false
        every { rs.getLong("Position") } returns serverPos
        if (serverGtidSet != null) {
            every { rs.getString("Executed_Gtid_Set") } returns serverGtidSet
        } else {
            every { rs.getString("Executed_Gtid_Set") } returns null
        }
        every { rs.metaData } returns rsMetaData
        every { rs.close() } returns Unit

        val stmt = mockk<Statement>()
        every { stmt.executeQuery("SHOW MASTER STATUS") } returns rs
        every { stmt.close() } returns Unit

        // Mock binary log names query
        val binaryLogsRs = mockk<ResultSet>()
        var binaryLogsIndex = 0
        every { binaryLogsRs.next() } answers
            {
                binaryLogsIndex < binaryLogFiles.size &&
                    run {
                        binaryLogsIndex++
                        true
                    }
            }
        binaryLogsIndex = 0
        every { binaryLogsRs.getString(1) } answers { binaryLogFiles[binaryLogsIndex - 1] }
        every { binaryLogsRs.close() } returns Unit
        every { stmt.executeQuery("SHOW BINARY LOGS") } returns binaryLogsRs

        val conn = mockk<Connection>()
        every { conn.createStatement() } returns stmt
        every { conn.close() } returns Unit

        val connFactory = mockk<io.airbyte.cdk.jdbc.JdbcConnectionFactory>()
        every { connFactory.get() } returns conn

        val cdcConfig = mockk<CdcIncrementalConfiguration>()
        every { cdcConfig.invalidCdcCursorPositionBehavior } returns behavior

        val config = mockk<MySqlSourceConfiguration>()
        every { config.incrementalConfiguration } returns cdcConfig
        every { config.namespaces } returns setOf("testdb")

        return MySqlSourceDebeziumOperations(connFactory, config)
    }

    @Test
    fun `deserializeState treats literal null gtids as absent and validates via binlog`() {
        // Scenario 1: Saved state has "gtids": null (NullNode.asText() == "null").
        // The fix should treat this as no GTIDs, and fall through to binlog validation.
        val ops =
            createOpsWithMockedJdbc(
                serverFile = "mysql-bin.000001",
                serverPos = 200,
                serverGtidSet = null,
                binaryLogFiles = listOf("mysql-bin.000001"),
            )
        val stateNode =
            buildStateNode(
                file = "mysql-bin.000001",
                pos = 154,
                gtidsExplicitNull = true,
            )
        val result = ops.deserializeState(stateNode)
        // With null GTIDs on both sides and matching binlog file, the state should be valid.
        assertTrue(
            result is ValidDebeziumWarmStartState,
            "Expected ValidDebeziumWarmStartState but got $result"
        )
    }

    @Test
    fun `deserializeState treats blank gtids string as absent`() {
        val ops =
            createOpsWithMockedJdbc(
                serverFile = "mysql-bin.000001",
                serverPos = 200,
                serverGtidSet = null,
                binaryLogFiles = listOf("mysql-bin.000001"),
            )
        val stateNode =
            buildStateNode(
                file = "mysql-bin.000001",
                pos = 154,
                gtids = "  ",
            )
        val result = ops.deserializeState(stateNode)
        assertTrue(
            result is ValidDebeziumWarmStartState,
            "Expected ValidDebeziumWarmStartState but got $result"
        )
    }

    @Test
    fun `deserializeState handles valid gtid set comparison`() {
        val gtid = "3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5"
        val ops =
            createOpsWithMockedJdbc(
                serverGtidSet = "3E11FA47-71CA-11E1-9E33-C80AA9429562:1-10",
            )
        val stateNode = buildStateNode(gtids = gtid)
        val result = ops.deserializeState(stateNode)
        assertTrue(
            result is ValidDebeziumWarmStartState,
            "Expected ValidDebeziumWarmStartState but got $result"
        )
    }

    @Test
    fun `deserializeState returns abort when saved gtid set not contained in server`() {
        val ops =
            createOpsWithMockedJdbc(
                serverGtidSet = "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA:1-5",
            )
        val stateNode =
            buildStateNode(
                gtids = "BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB:1-5",
            )
        val result = ops.deserializeState(stateNode)
        assertTrue(
            result is AbortDebeziumWarmStartState,
            "Expected AbortDebeziumWarmStartState but got $result"
        )
    }

    @Test
    fun `deserializeState aborts when saved state has gtids but server has none`() {
        val ops =
            createOpsWithMockedJdbc(
                serverGtidSet = null,
            )
        val stateNode =
            buildStateNode(
                gtids = "3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5",
            )
        val result = ops.deserializeState(stateNode)
        assertTrue(
            result is AbortDebeziumWarmStartState,
            "Expected AbortDebeziumWarmStartState but got $result"
        )
    }

    @Test
    fun `deserializeState returns reset when configured with RESET_SYNC behavior`() {
        val ops =
            createOpsWithMockedJdbc(
                serverGtidSet = null,
                behavior = InvalidCdcCursorPositionBehavior.RESET_SYNC,
            )
        val stateNode =
            buildStateNode(
                gtids = "3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5",
            )
        val result = ops.deserializeState(stateNode)
        assertTrue(
            result is ResetDebeziumWarmStartState,
            "Expected ResetDebeziumWarmStartState but got $result"
        )
    }

    @Test
    fun `deserializeState aborts when binlog file not found on server`() {
        val ops =
            createOpsWithMockedJdbc(
                serverFile = "mysql-bin.000003",
                serverPos = 200,
                serverGtidSet = null,
                binaryLogFiles = listOf("mysql-bin.000002", "mysql-bin.000003"),
            )
        val stateNode =
            buildStateNode(
                file = "mysql-bin.000001",
                pos = 154,
            )
        val result = ops.deserializeState(stateNode)
        assertTrue(
            result is AbortDebeziumWarmStartState,
            "Expected AbortDebeziumWarmStartState but got $result"
        )
    }
}
