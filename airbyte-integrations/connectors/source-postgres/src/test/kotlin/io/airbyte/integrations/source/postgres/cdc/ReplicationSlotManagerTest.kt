/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.debezium.connector.postgresql.connection.Lsn
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Unit tests for [ReplicationSlotManager.isAlreadyAdvanced].
 *
 * Regression coverage for the stall observed in airbytehq/oncall#12053, where a subsequent sync
 * re-acknowledged the same LSN that was already at `confirmed_flush_lsn` and opened a logical
 * replication stream that triggered a WAL-reclaim interaction on PostgreSQL 14. Once the slot is
 * already at or beyond the target LSN, `advanceLsn` must short-circuit instead of re-issuing
 * `setFlushedLSN`/`setAppliedLSN`.
 */
class ReplicationSlotManagerTest {

    @Test
    fun returnsTrueWhenConfirmedFlushLsnEqualsTarget() {
        val target = Lsn.valueOf(117488364080672L)
        assertTrue(ReplicationSlotManager.isAlreadyAdvanced(Lsn.valueOf(117488364080672L), target))
    }

    @Test
    fun returnsTrueWhenConfirmedFlushLsnIsAheadOfTarget() {
        val target = Lsn.valueOf(117488364080672L)
        assertTrue(ReplicationSlotManager.isAlreadyAdvanced(Lsn.valueOf(117488364080673L), target))
    }

    @Test
    fun returnsFalseWhenConfirmedFlushLsnIsBehindTarget() {
        val target = Lsn.valueOf(117488364080672L)
        assertFalse(ReplicationSlotManager.isAlreadyAdvanced(Lsn.valueOf(117469059140704L), target))
    }

    @Test
    fun returnsFalseWhenConfirmedFlushLsnIsNull() {
        val target = Lsn.valueOf(117488364080672L)
        assertFalse(ReplicationSlotManager.isAlreadyAdvanced(null, target))
    }
}
