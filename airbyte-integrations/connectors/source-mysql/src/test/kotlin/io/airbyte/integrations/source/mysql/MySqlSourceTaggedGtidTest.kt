/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.debezium.connector.mysql.gtid.MySqlGtidSet
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

/**
 * MySQL 8.4 allows GTIDs to carry a tag (WL#15294), e.g. `<uuid>:mysqlsh:1-42`. InnoDB Cluster
 * emits these for AdminAPI operations, and once present they stay in `gtid_executed` forever.
 *
 * [MySqlSourceDebeziumOperations] parses `gtid_executed` and `gtid_purged` into [MySqlGtidSet] to
 * decide whether the saved CDC position is still valid, so a parser that cannot read tags fails
 * every sync against such a server.
 *
 * See https://github.com/airbytehq/airbyte/issues/85846.
 */
class MySqlSourceTaggedGtidTest {

    companion object {
        const val UUID = "3e11fa47-71ca-11e1-9e33-c80aa9429562"
    }

    @Test
    fun testTaggedGtidSetIsParsed() {
        val gtidSet = MySqlGtidSet("$UUID:mysqlsh:1-42")
        assertEquals(1, gtidSet.uuidSets.size)
        assertEquals("$UUID:mysqlsh:1-42", gtidSet.toString())
    }

    /**
     * The tagged and untagged transactions of one server are distinct sets. Collapsing them onto
     * the bare UUID silently drops one of the two, which would let the connector skip transactions
     * it never read.
     */
    @Test
    fun testTaggedAndUntaggedSetsOfSameServerAreDistinct() {
        val gtidSet = MySqlGtidSet("$UUID:1-5:mysqlsh:1-3")
        assertEquals(2, gtidSet.uuidSets.size)
        assertEquals("$UUID:1-5:mysqlsh:1-3", gtidSet.toString())
    }

    @Test
    fun testContainmentIsTagAware() {
        val available = MySqlGtidSet("$UUID:1-5:mysqlsh:1-3")
        assertTrue(MySqlGtidSet("$UUID:1-5").isContainedWithin(available))
        assertTrue(MySqlGtidSet("$UUID:mysqlsh:1-3").isContainedWithin(available))
        // the untagged set does not vouch for the tagged transactions, nor the other way around
        assertFalse(MySqlGtidSet("$UUID:mysqlsh:1-3").isContainedWithin(MySqlGtidSet("$UUID:1-5")))
        assertFalse(MySqlGtidSet("$UUID:1-5").isContainedWithin(MySqlGtidSet("$UUID:mysqlsh:1-5")))
    }

    @Test
    fun testSubtractKeepsTagsApart() {
        val available = MySqlGtidSet("$UUID:1-5:mysqlsh:1-3")
        assertEquals("$UUID:mysqlsh:1-3", available.subtract(MySqlGtidSet("$UUID:1-5")).toString())
        assertEquals("$UUID:1-5", available.subtract(MySqlGtidSet("$UUID:mysqlsh:1-3")).toString())
    }

    @Test
    fun testUntaggedParsingIsUnchanged() {
        assertEquals("$UUID:1-199", MySqlGtidSet("$UUID:1-191:192-199").toString())
    }
}
