/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.debezium.connector.sqlserver.Lsn
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.Duration
import kotlin.test.assertContains
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MsSqlServerDebeziumOperationsTest {

    @Test
    fun `missing schema history is recovered from the saved offset`() {
        val configuration = cdcConfiguration()
        val operations =
            MsSqlServerDebeziumOperations(
                jdbcFactory(
                    configuration,
                    cdcResultSets = listOf(cdcTablesResultSet("dbo" to "users"))
                ),
                configuration
            )

        val warmStartState = operations.deserializeState(state())

        val validWarmStartState =
            assertInstanceOf(ValidDebeziumWarmStartState::class.java, warmStartState)
        assertNull(validWarmStartState.schemaHistory)

        val warmStartProperties = operations.generateWarmStartProperties(listOf(stream("users")))
        assertEquals("recovery", warmStartProperties["snapshot.mode"])
        assertEquals(
            "true",
            warmStartProperties["schema.history.internal.store.only.captured.tables.ddl"]
        )
        assertContains(warmStartProperties["table.include.list"] ?: "", "users")
    }

    @Test
    fun `schema history missing a CDC table routes through recovery`() {
        val configuration = cdcConfiguration()
        val operations =
            MsSqlServerDebeziumOperations(
                jdbcFactory(
                    configuration,
                    cdcResultSets =
                        listOf(
                            cdcTablesResultSet("dbo" to "users", "dbo" to "orders"),
                            cdcTablesResultSet("dbo" to "users", "dbo" to "orders"),
                        )
                ),
                configuration
            )

        val warmStartState =
            operations.deserializeState(state(schemaHistory = schemaHistoryFor("users")))

        val validWarmStartState =
            assertInstanceOf(ValidDebeziumWarmStartState::class.java, warmStartState)
        assertNull(validWarmStartState.schemaHistory)

        val warmStartProperties =
            operations.generateWarmStartProperties(listOf(stream("users"), stream("orders")))
        assertEquals("recovery", warmStartProperties["snapshot.mode"])
        assertContains(warmStartProperties["table.include.list"] ?: "", "users")
        assertContains(warmStartProperties["table.include.list"] ?: "", "orders")
        assertFalse(warmStartProperties.containsKey("column.include.list"))
    }

    @Test
    fun `complete schema history uses normal warm start mode`() {
        val configuration = cdcConfiguration()
        val operations =
            MsSqlServerDebeziumOperations(
                jdbcFactory(
                    configuration,
                    cdcResultSets = listOf(cdcTablesResultSet("dbo" to "users"))
                ),
                configuration
            )

        val warmStartState =
            operations.deserializeState(state(schemaHistory = schemaHistoryFor("users")))

        val validWarmStartState =
            assertInstanceOf(ValidDebeziumWarmStartState::class.java, warmStartState)
        assertEquals(1, validWarmStartState.schemaHistory?.wrapped?.size)

        val warmStartProperties = operations.generateWarmStartProperties(listOf(stream("users")))
        assertEquals("when_needed", warmStartProperties["snapshot.mode"])
    }

    private fun cdcConfiguration(): MsSqlServerSourceConfiguration =
        MsSqlServerSourceConfiguration(
            realHost = "localhost",
            realPort = 1433,
            sshTunnel = SshNoTunnelMethod,
            sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
            jdbcUrlFmt = "jdbc:sqlserver://%s:%d;databaseName=CdcTest",
            jdbcProperties =
                mapOf(
                    "user" to "sa",
                    "password" to "Password123!",
                    "authentication" to "SqlPassword",
                    "encrypt" to "false",
                    "trustServerCertificate" to "true",
                ),
            namespaces = setOf("dbo"),
            maxConcurrency = 1,
            checkpointTargetInterval = Duration.ofSeconds(300),
            checkPrivileges = true,
            debeziumHeartbeatInterval = Duration.ofSeconds(10),
            incrementalReplicationConfiguration =
                CdcIncrementalConfiguration(
                    initialWaitingSeconds = Duration.ofSeconds(300),
                    invalidCdcCursorPositionBehavior = InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                    initialLoadTimeout = Duration.ofHours(8),
                    pollIntervalMs = 500,
                ),
            databaseName = "CdcTest",
            authentication = SqlPasswordAuthentication("sa", "Password123!"),
        )

    private fun jdbcFactory(
        configuration: MsSqlServerSourceConfiguration,
        cdcResultSets: List<ResultSet> = emptyList()
    ): JdbcConnectionFactory {
        val connection = mockk<Connection>()
        val statement = mockk<Statement>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just runs
        every { statement.close() } just runs
        every { statement.executeQuery(any()) } returnsMany
            (listOf(validLsnResultSet()) + cdcResultSets)

        return object : JdbcConnectionFactory(configuration) {
            override fun get(): Connection = connection
        }
    }

    private fun validLsnResultSet(): ResultSet {
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns true
        every { resultSet.getBytes("min_lsn") } returns Lsn.valueOf(LSN).getBinary()
        every { resultSet.getBytes("max_lsn") } returns Lsn.valueOf(LSN).getBinary()
        every { resultSet.close() } just runs
        return resultSet
    }

    private fun cdcTablesResultSet(vararg tables: Pair<String, String>): ResultSet {
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returnsMany (tables.map { true } + false)
        every { resultSet.getString("schema_name") } returnsMany tables.map { it.first }
        every { resultSet.getString("table_name") } returnsMany tables.map { it.second }
        every { resultSet.close() } just runs
        return resultSet
    }

    private fun state(schemaHistory: String? = null) =
        Jsons.objectNode().apply {
            set<JsonNode>(
                MsSqlServerDebeziumOperations.MSSQL_STATE,
                Jsons.objectNode().apply {
                    set<JsonNode>(
                        MsSqlServerDebeziumOperations.MSSQL_CDC_OFFSET,
                        Jsons.objectNode().apply {
                            put(
                                """["CdcTest",{"server":"CdcTest","database":"CdcTest"}]""",
                                """{"event_serial_no":0,"commit_lsn":"$LSN","change_lsn":"NULL"}""",
                            )
                        }
                    )
                    schemaHistory?.let {
                        put(MsSqlServerDebeziumOperations.MSSQL_DB_HISTORY, it)
                    }
                }
            )
        }

    private fun schemaHistoryFor(vararg tables: String): String =
        tables.joinToString("\n") { table ->
            """{"source":{"server":"CdcTest","database":"CdcTest"},"position":{"commit_lsn":"$LSN"},"databaseName":"CdcTest","schemaName":"dbo","tableChanges":[{"type":"CREATE","id":"\"CdcTest\".\"dbo\".\"$table\"","table":{}}]}"""
        }

    private fun stream(name: String): Stream {
        val idField = io.airbyte.cdk.discover.EmittedField("id", IntFieldType)
        return Stream(
            id =
                StreamIdentifier.from(
                    StreamDescriptor()
                        .withName(name)
                        .withNamespace("dbo")
                ),
            schema = setOf(idField),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = listOf(idField),
            configuredCursor = null,
        )
    }

    private companion object {
        const val LSN = "0000002b:000003e0:0025"
    }
}
