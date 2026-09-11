/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.postgresql.connection.Lsn
import io.mockk.mockk
import org.apache.kafka.connect.source.SourceRecord
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class PostgresSourceDebeziumOperationsTest {
    private val operations =
        PostgresSourceDebeziumOperations(
            config = mockk(),
            connectionFactory = mockk(),
            replicationSlotManager = mockk(),
            startupState = null,
        )

    @Test
    fun `source record position preserves row and commit LSNs`() {
        val position = operations.position(sourceRecord(lsn = 100L, lsnCommit = 200L))!!

        assertEquals(Lsn.valueOf(200L), position.lsnCommit)
        assertEquals(Lsn.valueOf(100L), position.lsn)
        assertEquals(
            PostgresSourceDebeziumOperations.position(
                DebeziumOffset(
                    mapOf(
                        Jsons.objectNode() to
                            Jsons.objectNode().put("lsn", 100L).put("lsn_commit", 200L)
                    )
                )
            ),
            position,
        )
    }

    @Test
    fun `commit progress takes precedence over a decreasing row LSN`() {
        val previous = operations.position(sourceRecord(lsn = 190L, lsnCommit = 200L))!!
        val current = operations.position(sourceRecord(lsn = 110L, lsnCommit = 300L))!!

        assertTrue(current.compareTo(previous)!! > 0)
    }

    @Test
    fun `source record position uses row LSN to break a commit LSN tie`() {
        val current = operations.position(sourceRecord(lsn = 110L, lsnCommit = 200L))!!
        val previous =
            PostgresSourceCdcPosition(lsnCommit = Lsn.valueOf(200L), lsn = Lsn.valueOf(100L))

        assertTrue(current.compareTo(previous)!! > 0)
    }

    @Test
    fun `missing commit LSN leaves progress indeterminate`() {
        val current = operations.position(sourceRecord(lsn = 110L, lsnCommit = null))!!
        val previous =
            PostgresSourceCdcPosition(lsnCommit = Lsn.valueOf(200L), lsn = Lsn.valueOf(100L))

        assertNull(current.lsnCommit)
        assertEquals(Lsn.valueOf(110L), current.lsn)
        assertNull(current.compareTo(previous))
    }

    private fun sourceRecord(lsn: Long, lsnCommit: Long?): SourceRecord =
        SourceRecord(
            emptyMap<String, Any>(),
            buildMap {
                put("lsn", lsn)
                if (lsnCommit != null) put("lsn_commit", lsnCommit)
            },
            "test-topic",
            null,
            null,
        )
}
