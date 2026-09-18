/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.cdc.AbortDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ResetDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.mysql.gtid.MySqlGtidSet
import io.mockk.every
import io.mockk.mockk
import java.sql.Connection
import java.sql.ResultSet
import java.sql.ResultSetMetaData
import java.sql.Statement
import java.time.Duration
import kotlin.time.Duration.Companion.milliseconds
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Tests for GTID set validation in CDC warm-start, specifically covering the Debezium 3.1.x NPE in
 * MySqlGtidSet.subtract() when GTID sets contain server UUIDs absent from the other set (e.g.,
 * after MySQL failover/topology change).
 *
 * See: https://github.com/airbytehq/oncall/issues/12810 Upstream fix:
 * https://github.com/debezium/debezium/pull/6894 (DBZ-9682)
 */
class MySqlSourceGtidValidationTest {

    /**
     * Demonstrates the Debezium 3.1.x NPE bug in MySqlGtidSet.subtract(). When the source set
     * contains a server UUID not present in the other set, forServerWithId() returns null and the
     * subsequent getUUID() call NPEs.
     */
    @Test
    fun testDebeziumGtidSubtractNpeWithMismatchedUuids() {
        val available = MySqlGtidSet("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-10")
        val saved = MySqlGtidSet("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1-5")

        assertThrows(NullPointerException::class.java) { available.subtract(saved) }
    }

    /**
     * When the available GTID set contains UUIDs absent from the saved state (typical post-failover
     * scenario), the validate() method should catch the Debezium NPE and return
     * AbortDebeziumWarmStartState when FAIL_SYNC is configured.
     */
    @Test
    fun testValidateHandlesGtidNpeWithFailSync() {
        val ops =
            createOperations(
                serverGtids =
                    "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1-10," +
                        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-3",
                behavior = InvalidCdcCursorPositionBehavior.FAIL_SYNC,
            )

        val stateValue =
            buildOpaqueState(
                gtids = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1-5",
            )
        val result = ops.deserializeState(stateValue)

        assertInstanceOf(AbortDebeziumWarmStartState::class.java, result)
        val abortState = result as AbortDebeziumWarmStartState
        assertTrue(abortState.reason.contains("mismatched server UUIDs")) {
            "Expected reason to mention mismatched server UUIDs, got: ${abortState.reason}"
        }
    }

    /**
     * Same post-failover scenario but with RESET_SYNC — should return ResetDebeziumWarmStartState
     * so the platform can reset and re-snapshot.
     */
    @Test
    fun testValidateHandlesGtidNpeWithResetSync() {
        val ops =
            createOperations(
                serverGtids =
                    "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1-10," +
                        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-3",
                behavior = InvalidCdcCursorPositionBehavior.RESET_SYNC,
            )

        val stateValue =
            buildOpaqueState(
                gtids = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1-5",
            )
        val result = ops.deserializeState(stateValue)

        assertInstanceOf(ResetDebeziumWarmStartState::class.java, result)
        val resetState = result as ResetDebeziumWarmStartState
        assertTrue(resetState.reason.contains("mismatched server UUIDs")) {
            "Expected reason to mention mismatched server UUIDs, got: ${resetState.reason}"
        }
    }

    /**
     * When GTID sets have matching UUIDs and saved is contained within available, validation should
     * succeed normally (our defensive catches don't interfere).
     */
    @Test
    fun testValidateSucceedsWithMatchingGtidSets() {
        val ops =
            createOperations(
                serverGtids = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1-10",
                behavior = InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                purgedGtids = "",
            )

        val stateValue =
            buildOpaqueState(
                gtids = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1-5",
            )
        val result = ops.deserializeState(stateValue)

        assertInstanceOf(ValidDebeziumWarmStartState::class.java, result)
    }

    private fun createOperations(
        serverGtids: String,
        behavior: InvalidCdcCursorPositionBehavior,
        purgedGtids: String = "",
    ): MySqlSourceDebeziumOperations {
        val jdbcConnectionFactory = mockk<JdbcConnectionFactory>()

        // Each call to queryPositionAndGtids/queryPurgedIds opens a new connection via get().
        // Return a fresh mock connection each time to avoid use-after-close issues.
        every { jdbcConnectionFactory.get() } answers
            {
                createMockConnection(serverGtids, purgedGtids)
            }

        val configuration =
            MySqlSourceConfiguration(
                realHost = "localhost",
                realPort = 3306,
                sshTunnel = null,
                sshConnectionOptions =
                    SshConnectionOptions(
                        sessionHeartbeatInterval = 1000.milliseconds,
                        globalHeartbeatInterval = 2000.milliseconds,
                        idleTimeout = kotlin.time.Duration.ZERO,
                    ),
                jdbcUrlFmt = "jdbc:mysql://localhost:3306/test",
                jdbcProperties = mapOf("database" to "test"),
                namespaces = setOf("test"),
                tableFilters = emptyList(),
                incrementalConfiguration =
                    CdcIncrementalConfiguration(
                        initialLoadTimeout = Duration.ofHours(8),
                        serverTimezone = null,
                        invalidCdcCursorPositionBehavior = behavior,
                    ),
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofMinutes(15),
                checkPrivileges = false,
                treatTinyint1AsInteger = true,
            )

        return MySqlSourceDebeziumOperations(jdbcConnectionFactory, configuration)
    }

    private fun createMockConnection(
        serverGtids: String,
        purgedGtids: String,
    ): Connection {
        val connection = mockk<Connection>()
        val stmt = mockk<Statement>()

        // Mock SHOW MASTER STATUS result set
        val masterMeta = mockk<ResultSetMetaData>()
        every { masterMeta.columnCount } returns 5

        val masterStatusRs = mockk<ResultSet>()
        every { masterStatusRs.next() } returns true andThen false
        every { masterStatusRs.getString("File") } returns "mysql-bin.000001"
        every { masterStatusRs.wasNull() } returns false
        every { masterStatusRs.getLong("Position") } returns 154L
        every { masterStatusRs.getString("Executed_Gtid_Set") } returns serverGtids
        every { masterStatusRs.metaData } returns masterMeta
        every { masterStatusRs.close() } returns Unit

        // Mock @@global.gtid_purged result set
        val purgedRs = mockk<ResultSet>()
        every { purgedRs.next() } returns true andThen false
        every { purgedRs.getString("@@global.gtid_purged") } returns purgedGtids
        every { purgedRs.close() } returns Unit

        every { stmt.executeQuery("SHOW MASTER STATUS") } returns masterStatusRs
        every { stmt.executeQuery("SELECT @@global.gtid_purged") } returns purgedRs
        every { stmt.close() } returns Unit
        every { connection.createStatement() } returns stmt
        every { connection.close() } returns Unit

        return connection
    }

    /**
     * Builds an OpaqueStateValue matching the format expected by deserializeStateUnvalidated(): the
     * offset map has a single entry where both key and value are serialized as JSON strings.
     */
    private fun buildOpaqueState(
        gtids: String,
        file: String = "mysql-bin.000001",
        pos: Long = 154L,
    ): OpaqueStateValue {
        val topicPrefix = "test"
        val keyNode =
            Jsons.arrayNode().apply {
                add("test")
                add(Jsons.objectNode().apply { put("server", topicPrefix) })
            }
        val valueNode =
            Jsons.objectNode().apply {
                put("ts_sec", 1000L)
                put("file", file)
                put("pos", pos)
                put("gtids", gtids)
            }
        val offsetNode =
            Jsons.objectNode().apply {
                put(Jsons.writeValueAsString(keyNode), Jsons.writeValueAsString(valueNode))
            }
        return Jsons.objectNode().apply {
            set<ObjectNode>(
                "state",
                Jsons.objectNode().apply { set<ObjectNode>("mysql_cdc_offset", offsetNode) },
            )
        }
    }
}
