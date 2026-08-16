/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.mysql.gtid.MySqlGtidSet
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MySqlSourceDebeziumOperationsTest {

    @Test
    fun `missing gtids key is absent`() {
        assertNull(parseSavedGtids("""{"file":"binlog.000001","pos":4}"""))
    }

    @Test
    fun `json null gtids are treated as absent`() {
        assertNull(parseSavedGtids("""{"file":"binlog.000001","pos":4,"gtids":null}"""))
    }

    @Test
    fun `string null gtids are treated as absent`() {
        assertNull(parseSavedGtids("""{"file":"binlog.000001","pos":4,"gtids":"null"}"""))
    }

    @Test
    fun `empty string gtids are treated as absent`() {
        assertNull(parseSavedGtids("""{"file":"binlog.000001","pos":4,"gtids":""}"""))
    }

    @Test
    fun `whitespace gtids are treated as absent`() {
        assertNull(parseSavedGtids("""{"file":"binlog.000001","pos":4,"gtids":"   "}"""))
    }

    @Test
    fun `non-text gtids are treated as absent`() {
        assertNull(parseSavedGtids("""{"file":"binlog.000001","pos":4,"gtids":123}"""))
    }

    @Test
    fun `real gtid set is preserved`() {
        assertEquals(
            "uuid:1-10",
            parseSavedGtids("""{"file":"binlog.000001","pos":4,"gtids":"uuid:1-10"}"""),
        )
    }

    @Test
    fun `kotlin null saved gtid becomes an empty set`() {
        assertTrue(MySqlGtidSet(null as String?).isEmpty)
    }

    @Test
    fun `absent saved gtids use the binlog fallback`() {
        assertTrue(MySqlSourceDebeziumOperations.usesBinlogFallback(null))
        assertTrue(MySqlSourceDebeziumOperations.usesBinlogFallback(""))
        assertTrue(MySqlSourceDebeziumOperations.usesBinlogFallback("   "))
        assertTrue(
            MySqlSourceDebeziumOperations.usesBinlogFallback(
                parseSavedGtids("""{"file":"binlog.000001","pos":4,"gtids":null}""")
            )
        )
        assertTrue(
            MySqlSourceDebeziumOperations.usesBinlogFallback(
                parseSavedGtids("""{"file":"binlog.000001","pos":4,"gtids":"null"}""")
            )
        )
        assertFalse(MySqlSourceDebeziumOperations.usesBinlogFallback("uuid:1-10"))
    }

    @Test
    fun `empty saved gtid plus purged set does not abort warm start`() {
        val available = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-100"
        val purged = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-50"
        // Old path: empty saved set makes every server GTID look unseen, so purge overlap aborts.
        val saved = MySqlGtidSet(null as String?)
        val newGtidSet = MySqlGtidSet(available).subtract(saved)
        assertTrue(!newGtidSet.isEmpty)
        assertTrue(!newGtidSet.subtract(MySqlGtidSet(purged)).equals(newGtidSet))
        // New path: skip GTID checks when the parsed saved GTID is absent.
        assertFalse(
            MySqlSourceDebeziumOperations.purgedGtidsAbortWarmStart(null, available, purged)
        )
        assertFalse(
            MySqlSourceDebeziumOperations.purgedGtidsAbortWarmStart("", available, purged)
        )
        assertTrue(
            MySqlSourceDebeziumOperations.purgedGtidsAbortWarmStart(
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-10",
                available,
                purged,
            )
        )
    }

    private fun parseSavedGtids(offsetJson: String): String? {
        val key = Jsons.objectNode().put("server", "test")
        val value = Jsons.readTree(offsetJson)
        val state =
            MySqlSourceDebeziumOperations.Companion.UnvalidatedDeserializedState(
                DebeziumOffset(mapOf(key to value)),
            )
        return MySqlSourceDebeziumOperations.parseSavedOffset(state).gtidSet
    }
}
