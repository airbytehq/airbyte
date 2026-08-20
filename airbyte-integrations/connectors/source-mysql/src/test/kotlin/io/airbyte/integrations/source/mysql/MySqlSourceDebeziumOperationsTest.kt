/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
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
    fun `string null gtids are stripped from the warm-start offset`() {
        val sanitized = sanitizeOffset("""{"file":"binlog.000001","pos":4,"gtids":"null"}""")
        assertFalse(sanitized.has("gtids"))
        assertEquals("binlog.000001", sanitized["file"].asText())
        assertEquals(4, sanitized["pos"].asLong())
    }

    @Test
    fun `json null gtids are stripped from the warm-start offset`() {
        val sanitized = sanitizeOffset("""{"file":"binlog.000001","pos":4,"gtids":null}""")
        assertFalse(sanitized.has("gtids"))
    }

    @Test
    fun `blank gtids are stripped from the warm-start offset`() {
        val sanitized = sanitizeOffset("""{"file":"binlog.000001","pos":4,"gtids":"   "}""")
        assertFalse(sanitized.has("gtids"))
    }

    @Test
    fun `non-text gtids are stripped from the warm-start offset`() {
        val sanitized = sanitizeOffset("""{"file":"binlog.000001","pos":4,"gtids":123}""")
        assertFalse(sanitized.has("gtids"))
    }

    @Test
    fun `missing gtids stay missing on the warm-start offset`() {
        val sanitized = sanitizeOffset("""{"file":"binlog.000001","pos":4}""")
        assertFalse(sanitized.has("gtids"))
        assertEquals("binlog.000001", sanitized["file"].asText())
    }

    @Test
    fun `real gtid set is left on the warm-start offset`() {
        val sanitized =
            sanitizeOffset("""{"file":"binlog.000001","pos":4,"gtids":"uuid:1-10"}""")
        assertEquals("uuid:1-10", sanitized["gtids"].asText())
    }

    @Test
    fun `empty saved gtid plus purged set does not abort warm start`() {
        val available = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-100"
        val purged = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-50"
        // Debezium MySqlGtidSet.subtract NPEs when the saved set is empty. Even
        // without that, an empty saved set would treat every server GTID as unseen
        // and abort on gtid_purged overlap. Skip GTID checks when saved GTIDs are
        // absent; keep aborting when a real saved set is behind purged GTIDs.
        assertFalse(
            MySqlSourceDebeziumOperations.purgedGtidsAbortWarmStart(null, available, purged)
        )
        assertFalse(MySqlSourceDebeziumOperations.purgedGtidsAbortWarmStart("", available, purged))
        assertTrue(
            MySqlSourceDebeziumOperations.purgedGtidsAbortWarmStart(
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-10",
                available,
                purged,
            )
        )
        assertFalse(
            MySqlSourceDebeziumOperations.purgedGtidsAbortWarmStart(
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:1-100",
                available,
                purged,
            )
        )
    }

    private fun parseSavedGtids(offsetJson: String): String? {
        return MySqlSourceDebeziumOperations.parseSavedOffset(offsetState(offsetJson)).gtidSet
    }

    private fun sanitizeOffset(offsetJson: String): JsonNode {
        val offset = offsetState(offsetJson).offset
        return MySqlSourceDebeziumOperations.offsetWithoutUnusableGtids(offset)
            .wrapped
            .values
            .first()
    }

    private fun offsetState(
        offsetJson: String
    ): MySqlSourceDebeziumOperations.Companion.UnvalidatedDeserializedState {
        val key = Jsons.objectNode().put("server", "test")
        val value = Jsons.readTree(offsetJson)
        return MySqlSourceDebeziumOperations.Companion.UnvalidatedDeserializedState(
            DebeziumOffset(mapOf(key to value)),
        )
    }
}
