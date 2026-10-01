/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.util.Jsons
import io.debezium.config.Configuration
import io.debezium.connector.sqlserver.SqlServerConnectorConfig
import io.debezium.relational.history.HistoryRecord
import io.mockk.mockk
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

    @Test
    fun `heartbeat offset excludes streamed ALTER record`() {
        assertFalse(comparator.isAtOrBefore(record(ALTER_CHANGE), record(heartbeatOffset)))
    }

    @Test
    fun `normalized heartbeat offset includes streamed ALTER record`() {
        assertTrue(comparator.isAtOrBefore(record(ALTER_CHANGE), record(normalized())))
    }

    @Test
    fun `snapshot record is included by both offsets`() {
        assertTrue(comparator.isAtOrBefore(record("NULL"), record(heartbeatOffset)))
        assertTrue(comparator.isAtOrBefore(record("NULL"), record(normalized())))
    }

    @Test
    fun `normalized heartbeat offset excludes records after commit_lsn`() {
        assertFalse(comparator.isAtOrBefore(record(LATER_CHANGE), record(normalized())))
    }

    private fun normalized(): Map<String, Any?> {
        val operations =
            MsSqlServerDebeziumOperations(
                mockk<JdbcConnectionFactory>(relaxed = true),
                MsSqlServerSourceConfigurationFactory()
                    .make(
                        MsSqlServerSourceConfigurationSpecification().apply {
                            host = "localhost"
                            port = 1433
                            database = "test"
                            username = "sa"
                            password = "Password123!"
                            setIncrementalValue(Cdc())
                        }
                    ),
            )
        val offset =
            DebeziumOffset(
                mapOf(Jsons.readTree("""["test"]""") to Jsons.valueToTree(heartbeatOffset))
            )
        val value = operations.normalizeHeartbeatChangeLsn(offset).wrapped.values.first()
        @Suppress("UNCHECKED_CAST")
        return Jsons.treeToValue(value, Map::class.java) as Map<String, Any?>
    }

    private fun record(changeLsn: String): HistoryRecord =
        record(mapOf("commit_lsn" to changeLsn, "change_lsn" to changeLsn))

    private fun record(position: Map<String, Any?>): HistoryRecord =
        HistoryRecord(SOURCE, position, null, null, null, null, null)

    companion object {
        private val SOURCE = mapOf("server" to "test", "database" to "test")
        private const val ALTER_CHANGE = "00033e76:0000cd50:0002"
        private const val COMMIT = "00033e76:0000cd58:0008"
        private const val LATER_CHANGE = "00033e76:0000cd60:0001"
    }
}
