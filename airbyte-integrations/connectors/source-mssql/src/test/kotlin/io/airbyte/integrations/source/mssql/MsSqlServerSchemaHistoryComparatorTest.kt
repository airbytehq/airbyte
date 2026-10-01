/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.util.Jsons
import io.debezium.config.Configuration
import io.debezium.connector.sqlserver.SqlServerConnectorConfig
import io.debezium.relational.history.HistoryRecord
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Pins Debezium's SQL Server schema-history comparator, which decides which history records are
 * replayed on warm start. It compares change_lsn only, which is why a heartbeat offset (change_lsn
 * = NULL) drops every streamed ALTER record (airbytehq/oncall#13544).
 */
class MsSqlServerSchemaHistoryComparatorTest {

    private val comparator =
        SqlServerConnectorConfig(
                Configuration.create()
                    .with("topic.prefix", "test")
                    .with("database.names", "test")
                    .build()
            )
            .historyRecordComparator

    private val heartbeatOffset =
        mapOf("commit_lsn" to COMMIT, "change_lsn" to "NULL", "event_serial_no" to 0)

    // Positions are realistic (commit_lsn >= change_lsn) so these tests stay meaningful if
    // Debezium ever starts comparing commit_lsn too.
    private val snapshotRecord = record(commitLsn = SNAPSHOT_COMMIT, changeLsn = "NULL")
    private val alterRecord = record(commitLsn = ALTER_COMMIT, changeLsn = ALTER_CHANGE)
    private val laterRecord = record(commitLsn = LATER_COMMIT, changeLsn = LATER_CHANGE)

    @Test
    fun `heartbeat offset excludes streamed ALTER record`() {
        assertFalse(comparator.isAtOrBefore(alterRecord, record(heartbeatOffset)))
    }

    @Test
    fun `normalized heartbeat offset includes streamed ALTER record`() {
        assertTrue(comparator.isAtOrBefore(alterRecord, record(normalized())))
    }

    @Test
    fun `snapshot record is included by both offsets`() {
        assertTrue(comparator.isAtOrBefore(snapshotRecord, record(heartbeatOffset)))
        assertTrue(comparator.isAtOrBefore(snapshotRecord, record(normalized())))
    }

    @Test
    fun `normalized heartbeat offset excludes records after commit_lsn`() {
        assertFalse(comparator.isAtOrBefore(laterRecord, record(normalized())))
    }

    /** [heartbeatOffset] after normalizeHeartbeatChangeLsn, which works on JSON, as a map. */
    private fun normalized(): Map<String, Any?> {
        val offset =
            DebeziumOffset(
                mapOf(Jsons.readTree("""["test"]""") to Jsons.valueToTree(heartbeatOffset))
            )
        val value =
            debeziumOperationsWithoutDatabase()
                .normalizeHeartbeatChangeLsn(offset)
                .wrapped
                .values
                .first()
        @Suppress("UNCHECKED_CAST")
        return Jsons.treeToValue(value, Map::class.java) as Map<String, Any?>
    }

    private fun record(commitLsn: String, changeLsn: String): HistoryRecord =
        record(mapOf("commit_lsn" to commitLsn, "change_lsn" to changeLsn))

    private fun record(position: Map<String, Any?>): HistoryRecord =
        HistoryRecord(SOURCE, position, null, null, null, null, null)

    companion object {
        private val SOURCE = mapOf("server" to "test", "database" to "test")
        private const val SNAPSHOT_COMMIT = "00033e76:0000cd40:0001"
        private const val ALTER_CHANGE = "00033e76:0000cd50:0002"
        private const val ALTER_COMMIT = "00033e76:0000cd52:0004"
        private const val COMMIT = "00033e76:0000cd58:0008"
        private const val LATER_CHANGE = "00033e76:0000cd60:0001"
        private const val LATER_COMMIT = "00033e76:0000cd60:0003"
    }
}
