/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.cdk.read.cdc.AbortDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ResetDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.InvalidCdcCursorPositionBehavior
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.debezium.connector.postgresql.connection.Lsn
import io.mockk.every
import io.mockk.mockk
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class PostgresSourceDebeziumOperationsTest {

    private fun buildOpaqueState(lsn: Long): com.fasterxml.jackson.databind.JsonNode {
        val offsetKey = """["testdb",{"server":"testdb"}]"""
        val offsetValue = """{"lsn_proc":$lsn,"lsn":$lsn,"lsn_commit":$lsn}"""
        return Jsons.objectNode().apply {
            set<com.fasterxml.jackson.databind.JsonNode>(
                "state",
                Jsons.objectNode().put(offsetKey, offsetValue)
            )
        }
    }

    private fun createOperations(
        behavior: InvalidCdcCursorPositionBehavior,
        slotValidationResult: ReplicationSlotManager.SlotValidationResult,
    ): PostgresSourceDebeziumOperations {
        val cdcConfig =
            CdcIncrementalConfiguration(
                initialLoadTimeout = Duration.ofHours(8),
                invalidCdcCursorPositionBehavior = behavior,
                shutdownTimeout = Duration.ofMinutes(5),
                replicationSlot = "test_slot",
                publication = "test_pub",
                debeziumCommitsLsn = false,
                heartbeatActionQuery = null,
                airbyteHeartbeatTimeout = Duration.ofMinutes(10),
            )
        val config: PostgresSourceConfiguration = mockk {
            every { cdc } returns cdcConfig
            every { database } returns "testdb"
        }
        val connectionFactory: PostgresSourceJdbcConnectionFactory = mockk()
        val replicationSlotManager: ReplicationSlotManager = mockk {
            every { checkSlotValidity(any()) } returns slotValidationResult
        }
        return PostgresSourceDebeziumOperations(
            config = config,
            connectionFactory = connectionFactory,
            replicationSlotManager = replicationSlotManager,
            startupState = null,
        )
    }

    @Test
    fun `deserializeState returns ValidDebeziumWarmStartState when slot is valid`() {
        val ops =
            createOperations(
                InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                ReplicationSlotManager.SlotValidationResult.Valid,
            )
        val state = buildOpaqueState(100L)
        val result = ops.deserializeState(state)
        assertTrue(result is ValidDebeziumWarmStartState)
    }

    @Test
    fun `deserializeState returns AbortDebeziumWarmStartState when slot is invalid and behavior is FAIL_SYNC`() {
        val reason = "Replication slot 'test_slot' is not valid: wal_status = 'lost'."
        val ops =
            createOperations(
                InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                ReplicationSlotManager.SlotValidationResult.Invalid(reason),
            )
        val state = buildOpaqueState(100L)
        val result = ops.deserializeState(state)
        assertTrue(result is AbortDebeziumWarmStartState)
        assertEquals(reason, (result as AbortDebeziumWarmStartState).reason)
    }

    @Test
    fun `deserializeState returns ResetDebeziumWarmStartState when slot is invalid and behavior is RESET_SYNC`() {
        val reason = "Replication slot 'test_slot' is not valid: wal_status = 'lost'."
        val ops =
            createOperations(
                InvalidCdcCursorPositionBehavior.RESET_SYNC,
                ReplicationSlotManager.SlotValidationResult.Invalid(reason),
            )
        val state = buildOpaqueState(100L)
        val result = ops.deserializeState(state)
        assertTrue(result is ResetDebeziumWarmStartState)
        assertEquals(reason, (result as ResetDebeziumWarmStartState).reason)
    }

    @Test
    fun `deserializeState returns AbortDebeziumWarmStartState when state cannot be deserialized`() {
        val ops =
            createOperations(
                InvalidCdcCursorPositionBehavior.RESET_SYNC,
                ReplicationSlotManager.SlotValidationResult.Valid,
            )
        val invalidState = Jsons.objectNode().put("state", "not_an_object")
        val result = ops.deserializeState(invalidState)
        assertTrue(result is AbortDebeziumWarmStartState)
    }

    @Test
    fun `deserializeState returns ResetDebeziumWarmStartState when slot has advanced past saved LSN`() {
        val reason =
            "Replication slot 'test_slot' has advanced beyond the source's state LSN. " +
                "Confirmed flush LSN: 0/200, source LSN: 0/100."
        val ops =
            createOperations(
                InvalidCdcCursorPositionBehavior.RESET_SYNC,
                ReplicationSlotManager.SlotValidationResult.Invalid(reason),
            )
        val state = buildOpaqueState(100L)
        val result = ops.deserializeState(state)
        assertTrue(result is ResetDebeziumWarmStartState)
        assertEquals(reason, (result as ResetDebeziumWarmStartState).reason)
    }
}
