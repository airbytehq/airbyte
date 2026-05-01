/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.cdc.AbortDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.sqlserver.Lsn
import io.mockk.every
import io.mockk.mockk
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

/**
 * Tests for LSN validation logic in [MsSqlServerDebeziumOperations.deserializeState], specifically
 * the fix for unauthorized CDC capture instances causing false validation failures.
 *
 * When sys.fn_cdc_get_min_lsn() is called on an unauthorized capture instance it returns
 * 0x00000000000000000000. Without NULLIF, MIN() across all instances would return zero, triggering
 * a spurious "LSN invalid" abort even when authorized instances have valid LSNs.
 */
class MsSqlServerLsnValidationTest {

    private lateinit var mockJdbcConnectionFactory: JdbcConnectionFactory
    private lateinit var mockConnection: Connection
    private lateinit var mockStatement: Statement
    private lateinit var mockResultSet: ResultSet
    private lateinit var configuration: MsSqlServerSourceConfiguration

    private val zeroLsnBytes = ByteArray(10) // 10 bytes of zeros = 0x00000000000000000000

    @BeforeEach
    fun setUp() {
        mockResultSet = mockk(relaxed = true)
        mockStatement =
            mockk(relaxed = true) {
                every { executeQuery(any()) } returns mockResultSet
                every { close() } returns Unit
            }
        mockConnection =
            mockk(relaxed = true) {
                every { createStatement() } returns mockStatement
                every { close() } returns Unit
            }
        mockJdbcConnectionFactory = mockk { every { get() } returns mockConnection }
        configuration =
            mockk(relaxed = true) {
                every { incrementalReplicationConfiguration } returns
                    CdcIncrementalConfiguration(
                        initialWaitingSeconds = Duration.ofSeconds(300),
                        invalidCdcCursorPositionBehavior =
                            InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                        initialLoadTimeout = Duration.ofHours(8),
                        pollIntervalMs = 500
                    )
                every { databaseName } returns "test_db"
            }
    }

    private fun createDebeziumOps(): MsSqlServerDebeziumOperations {
        return MsSqlServerDebeziumOperations(mockJdbcConnectionFactory, configuration)
    }

    /**
     * Builds a minimal opaque state JSON that [MsSqlServerDebeziumOperations.deserializeState] can
     * parse. The state embeds a single offset entry with the given commit_lsn and a non-empty
     * schema history so that only the LSN validation path is exercised.
     */
    private fun buildStateJson(commitLsn: String): com.fasterxml.jackson.databind.JsonNode {
        val offsetKey = Jsons.objectNode().apply { put("server", "test_db") }
        val offsetValue =
            Jsons.objectNode().apply {
                put("commit_lsn", commitLsn)
                put("change_lsn", commitLsn)
                put("event_serial_no", 1)
            }
        val offsetNode =
            Jsons.objectNode().apply {
                put(Jsons.writeValueAsString(offsetKey), Jsons.writeValueAsString(offsetValue))
            }
        val stateNode =
            Jsons.objectNode().apply {
                set<ObjectNode>("mssql_cdc_offset", offsetNode)
                put("mssql_db_history", "{}")
                put("is_compressed", false)
            }
        return Jsons.objectNode().apply { set<ObjectNode>("state", stateNode) }
    }

    @Test
    fun `LSN validation succeeds when all capture instances are authorized`() {
        val savedLsn = "00000025:00000728:0005"
        val minLsnBytes = Lsn.valueOf(savedLsn).binary
        val maxLsnBytes = Lsn.valueOf("00000030:00000900:0001").binary

        every { mockResultSet.next() } returns true
        every { mockResultSet.getBytes("min_lsn") } returns minLsnBytes
        every { mockResultSet.getBytes("max_lsn") } returns maxLsnBytes
        every { mockResultSet.getInt("total_instances") } returns 3
        every { mockResultSet.getInt("unauthorized_instances") } returns 0

        val ops = createDebeziumOps()
        val state = buildStateJson(savedLsn)
        val result = ops.deserializeState(state)

        assertInstanceOf(ValidDebeziumWarmStartState::class.java, result)
    }

    @Test
    fun `LSN validation succeeds with some unauthorized capture instances via NULLIF`() {
        val savedLsn = "00000025:00000728:0005"
        val minLsnBytes = Lsn.valueOf(savedLsn).binary
        val maxLsnBytes = Lsn.valueOf("00000030:00000900:0001").binary

        // Simulate: 5 total instances, 2 unauthorized (NULLIF excludes them from MIN)
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBytes("min_lsn") } returns minLsnBytes
        every { mockResultSet.getBytes("max_lsn") } returns maxLsnBytes
        every { mockResultSet.getInt("total_instances") } returns 5
        every { mockResultSet.getInt("unauthorized_instances") } returns 2

        val ops = createDebeziumOps()
        val state = buildStateJson(savedLsn)
        val result = ops.deserializeState(state)

        assertInstanceOf(ValidDebeziumWarmStartState::class.java, result)
    }

    @Test
    fun `LSN validation fails when all capture instances are unauthorized`() {
        val savedLsn = "00000025:00000728:0005"
        val maxLsnBytes = Lsn.valueOf("00000030:00000900:0001").binary

        // When all instances are unauthorized, NULLIF makes MIN() return NULL
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBytes("min_lsn") } returns null
        every { mockResultSet.getBytes("max_lsn") } returns maxLsnBytes
        every { mockResultSet.getInt("total_instances") } returns 3
        every { mockResultSet.getInt("unauthorized_instances") } returns 3

        val ops = createDebeziumOps()
        val state = buildStateJson(savedLsn)
        val result = ops.deserializeState(state)

        assertInstanceOf(AbortDebeziumWarmStartState::class.java, result)
    }

    @Test
    fun `LSN validation fails when no capture instances exist`() {
        val savedLsn = "00000025:00000728:0005"
        val maxLsnBytes = Lsn.valueOf("00000030:00000900:0001").binary

        every { mockResultSet.next() } returns true
        every { mockResultSet.getBytes("min_lsn") } returns null
        every { mockResultSet.getBytes("max_lsn") } returns maxLsnBytes
        every { mockResultSet.getInt("total_instances") } returns 0
        every { mockResultSet.getInt("unauthorized_instances") } returns 0

        val ops = createDebeziumOps()
        val state = buildStateJson(savedLsn)
        val result = ops.deserializeState(state)

        assertInstanceOf(AbortDebeziumWarmStartState::class.java, result)
    }

    @Test
    fun `LSN validation fails when saved LSN is outside valid range`() {
        val savedLsn = "00000010:00000100:0001"
        val minLsnBytes = Lsn.valueOf("00000020:00000500:0001").binary
        val maxLsnBytes = Lsn.valueOf("00000030:00000900:0001").binary

        every { mockResultSet.next() } returns true
        every { mockResultSet.getBytes("min_lsn") } returns minLsnBytes
        every { mockResultSet.getBytes("max_lsn") } returns maxLsnBytes
        every { mockResultSet.getInt("total_instances") } returns 3
        every { mockResultSet.getInt("unauthorized_instances") } returns 0

        val ops = createDebeziumOps()
        val state = buildStateJson(savedLsn)
        val result = ops.deserializeState(state)

        assertInstanceOf(AbortDebeziumWarmStartState::class.java, result)
    }

    @Test
    fun `LSN validation fails when CDC is not enabled`() {
        val savedLsn = "00000025:00000728:0005"

        // maxLsnBytes null means CDC is not enabled
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBytes("min_lsn") } returns null
        every { mockResultSet.getBytes("max_lsn") } returns null
        every { mockResultSet.getInt("total_instances") } returns 0
        every { mockResultSet.getInt("unauthorized_instances") } returns 0

        val ops = createDebeziumOps()
        val state = buildStateJson(savedLsn)
        val result = ops.deserializeState(state)

        assertInstanceOf(AbortDebeziumWarmStartState::class.java, result)
    }

    @Test
    fun `verify NULLIF query structure excludes zero LSN from MIN aggregation`() {
        // This test verifies the SQL query contains the NULLIF pattern.
        // We capture the query executed and assert its structure.
        var capturedQuery: String? = null
        every { mockStatement.executeQuery(any()) } answers
            {
                capturedQuery = firstArg()
                mockResultSet
            }

        val savedLsn = "00000025:00000728:0005"
        val minLsnBytes = Lsn.valueOf(savedLsn).binary
        val maxLsnBytes = Lsn.valueOf("00000030:00000900:0001").binary

        every { mockResultSet.next() } returns true
        every { mockResultSet.getBytes("min_lsn") } returns minLsnBytes
        every { mockResultSet.getBytes("max_lsn") } returns maxLsnBytes
        every { mockResultSet.getInt("total_instances") } returns 1
        every { mockResultSet.getInt("unauthorized_instances") } returns 0

        val ops = createDebeziumOps()
        val state = buildStateJson(savedLsn)
        ops.deserializeState(state)

        assertTrue(capturedQuery != null, "SQL query should have been executed")
        assertTrue(
            capturedQuery!!.contains(
                "NULLIF(sys.fn_cdc_get_min_lsn(capture_instance), 0x00000000000000000000)"
            ),
            "Query must use NULLIF to exclude unauthorized (zero) LSN values from MIN()"
        )
        assertTrue(
            capturedQuery!!.contains("unauthorized_instances"),
            "Query must count unauthorized instances for diagnostics"
        )
    }
}
