/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.util.Jsons
import io.mockk.mockk
import java.time.Duration
import kotlin.time.Duration.Companion.ZERO
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class MsSqlServerDebeziumOperationsTest {

    private val operations =
        MsSqlServerDebeziumOperations(
            mockk<JdbcConnectionFactory>(),
            MsSqlServerSourceConfiguration(
                realHost = "localhost",
                realPort = 1433,
                sshTunnel = SshNoTunnelMethod,
                sshConnectionOptions = SshConnectionOptions(ZERO, ZERO, ZERO),
                jdbcUrlFmt = "jdbc:sqlserver://%s:%d;databaseName=test",
                jdbcProperties = emptyMap(),
                namespaces = setOf("dbo"),
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofMinutes(5),
                checkPrivileges = false,
                incrementalReplicationConfiguration =
                    CdcIncrementalConfiguration(
                        initialWaitingSeconds = Duration.ofSeconds(5),
                        invalidCdcCursorPositionBehavior = InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                        initialLoadTimeout = Duration.ofHours(1),
                        pollIntervalMs = 1000,
                    ),
                databaseName = "test",
                authentication = SqlPasswordAuthentication("sa", "password"),
            ),
        )

    @Test
    fun advancesIdleOffsetToSyncUpperBound() {
        val startingOffset = offset("0000002b:000003e0:0025", "NULL", 0)
        val upperBound = MsSqlServerCdcPosition("0000002c:00000210:0003")

        val actual =
            operations.advanceIdleOffset(
                startingOffset,
                startingOffset,
                upperBound,
            )
        val actualValue = actual.wrapped.values.first()

        assertEquals(upperBound.lsn, actualValue["commit_lsn"].asText())
        assertEquals("NULL", actualValue["change_lsn"].asText())
        assertEquals(0, actualValue["event_serial_no"].asInt())
    }

    @Test
    fun leavesProgressedOffsetUnchanged() {
        val startingOffset = offset("0000002b:000003e0:0025", "NULL", 0)
        val progressedOffset =
            offset("0000002b:000003e0:0026", "0000002b:000003e0:0024", 1)

        val actual =
            operations.advanceIdleOffset(
                progressedOffset,
                startingOffset,
                MsSqlServerCdcPosition("0000002c:00000210:0003"),
            )

        assertEquals(progressedOffset, actual)
    }

    @Test
    fun leavesOffsetUnchangedWhenDebeziumUpdatedOffsetContents() {
        val startingOffset = offset("0000002b:000003e0:0025", "NULL", 0)
        val updatedOffset = offset("0000002b:000003e0:0025", "0000002b:000003e0:0024", 1)

        val actual =
            operations.advanceIdleOffset(
                updatedOffset,
                startingOffset,
                MsSqlServerCdcPosition("0000002c:00000210:0003"),
            )

        assertEquals(updatedOffset, actual)
    }

    private fun offset(commitLsn: String, changeLsn: String, eventSerialNo: Int): DebeziumOffset =
        DebeziumOffset(
            mapOf(
                Jsons.arrayNode()
                    .add("test")
                    .add(Jsons.objectNode().put("server", "test").put("database", "test")) to
                    Jsons.objectNode()
                        .put("commit_lsn", commitLsn)
                        .put("change_lsn", changeLsn)
                        .put("event_serial_no", eventSerialNo)
            )
        )
}
