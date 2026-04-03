/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.util.Jsons
import io.mockk.every
import io.mockk.mockk
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.Duration
import kotlin.test.assertIs
import org.junit.jupiter.api.Test

class MySqlSourceDebeziumOperationsTest {
    @Test
    fun `deserializeState treats string null gtids as absent`() {
        val jdbcConnectionFactory = mockk<JdbcConnectionFactory>()
        val connection = mockk<Connection>()
        val statement = mockk<Statement>()
        val masterStatus = mockk<ResultSet>()
        val binaryLogs = mockk<ResultSet>()

        every { jdbcConnectionFactory.get() } returns connection
        every { connection.createStatement() } returns statement
        every { connection.close() } returns Unit
        every { statement.close() } returns Unit
        every { statement.executeQuery("SHOW MASTER STATUS") } returns masterStatus
        every { statement.executeQuery("SHOW BINARY LOGS") } returns binaryLogs
        every { masterStatus.close() } returns Unit
        every { binaryLogs.close() } returns Unit

        every { masterStatus.next() } returnsMany listOf(true, false)
        every { masterStatus.getString("File") } returns "mysql-bin.000001"
        every { masterStatus.getLong("Position") } returns 123L
        every { masterStatus.getString("Executed_Gtid_Set") } returns null
        every { masterStatus.wasNull() } returnsMany listOf(false, false, true)
        every { masterStatus.metaData.columnCount } returns 5

        every { binaryLogs.next() } returnsMany listOf(true, false)
        every { binaryLogs.getString(1) } returns "mysql-bin.000001"

        val operations = MySqlSourceDebeziumOperations(jdbcConnectionFactory, cdcConfiguration())

        val state: OpaqueStateValue =
            Jsons.readTree(
                """
                {
                  "state": {
                    "mysql_cdc_offset": {
                      "[\"db\",{\"server\":\"test\"}]": "{\"file\":\"mysql-bin.000001\",\"pos\":123,\"gtids\":\"null\"}"
                    }
                  }
                }
                """.trimIndent()
            )

        val result = operations.deserializeState(state)

        assertIs<ValidDebeziumWarmStartState>(result)
    }

    private fun cdcConfiguration(): MySqlSourceConfiguration {
        val configSpec =
            MySqlSourceConfigurationSpecification().apply {
                host = "localhost"
                port = 3306
                username = "user"
                password = "password"
                database = "db"
                checkpointTargetIntervalSeconds = 60
                concurrency = 1
                setIncrementalValue(Cdc())
            }

        return MySqlSourceConfigurationFactory()
            .make(configSpec)
            .copy(
                incrementalConfiguration =
                    CdcIncrementalConfiguration(
                        initialLoadTimeout = Duration.ofMinutes(5),
                        serverTimezone = null,
                        invalidCdcCursorPositionBehavior =
                            InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                    )
            )
    }
}
