/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres.cdc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.debezium.connector.postgresql.connection.Lsn
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Test

class PostgresSourceDebeziumOperationsValidateTest {

    private val cdcConfig =
        mockk<CdcIncrementalConfiguration>(relaxed = true) {
            every { debeziumCommitsLsn } returns false
        }
    private val config =
        mockk<PostgresSourceConfiguration>(relaxed = true) { every { cdc } returns cdcConfig }
    private val replicationSlotManager = mockk<ReplicationSlotManager>(relaxed = true)

    private val ops =
        PostgresSourceDebeziumOperations(
            config = config,
            connectionFactory = mockk<PostgresSourceJdbcConnectionFactory>(relaxed = true),
            replicationSlotManager = replicationSlotManager,
            startupState = null,
        )

    private fun offset(lsn: Long, lsnProc: Long, lsnCommit: Long?): DebeziumOffset {
        val key: JsonNode = Jsons.arrayNode().add("db").add(Jsons.objectNode().put("server", "db"))
        val value =
            Jsons.objectNode()
                .put("lsn", lsn)
                .put("lsn_proc", lsnProc)
                .put("txId", 1L)
                .put("ts_usec", 1L)
        if (lsnCommit != null) {
            value.put("lsn_commit", lsnCommit)
        }
        return DebeziumOffset(mapOf(key to value))
    }

    @Test
    fun `startup validates the slot against lsn_commit for an offset inside a long transaction`() {
        // The offset points at an INSERT written early in a long transaction (lsn), while the
        // transaction's commit record (lsn_commit) is several GB of WAL later. A slot that the
        // previous sync flushed to a position between the two still has every unread change.
        val insideLongTransaction = 370_015_497_820_088L
        val commitOfLongTransaction = 370_025_198_049_304L

        ops.startup(offset(insideLongTransaction, insideLongTransaction, commitOfLongTransaction))

        verify { replicationSlotManager.validate(Lsn.valueOf(commitOfLongTransaction)) }
    }

    @Test
    fun `startup validates the slot against lsn when the offset has no lsn_commit`() {
        val lsn = 3_575_761_602_216L

        ops.startup(offset(lsn, lsn, lsnCommit = null))

        verify { replicationSlotManager.validate(Lsn.valueOf(lsn)) }
    }
}
