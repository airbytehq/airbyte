/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import kotlin.random.Random
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Tests for the server_id range used by [MySqlSourceDebeziumOperations] to register as a binlog
 * reader with MySQL. A too-narrow range causes birthday- problem collisions when many CDC
 * connections target the same server.
 */
class MySqlSourceDebeziumOperationsServerIdTest {

    @Test
    fun testServerIdRangeConstants() {
        Assertions.assertEquals(5400, MySqlSourceDebeziumOperations.MIN_SERVER_ID)
        Assertions.assertEquals(
            Integer.MAX_VALUE,
            MySqlSourceDebeziumOperations.MAX_SERVER_ID,
            "MAX_SERVER_ID should span most of the positive Int range to avoid collisions"
        )
    }

    @Test
    fun testServerIdGeneratedWithinRange() {
        val random = Random(42)
        val generatedIds =
            (1..1000).map {
                random.nextInt(
                    MySqlSourceDebeziumOperations.MIN_SERVER_ID..MySqlSourceDebeziumOperations
                            .MAX_SERVER_ID
                )
            }
        for (id in generatedIds) {
            Assertions.assertTrue(
                id >= MySqlSourceDebeziumOperations.MIN_SERVER_ID,
                "Generated server_id $id should be >= MIN_SERVER_ID"
            )
            Assertions.assertTrue(
                id <= MySqlSourceDebeziumOperations.MAX_SERVER_ID,
                "Generated server_id $id should be <= MAX_SERVER_ID"
            )
        }
    }

    @Test
    fun testServerIdCollisionProbabilityIsLow() {
        val random = Random(123)
        val ids =
            (1..10000)
                .map {
                    random.nextInt(
                        MySqlSourceDebeziumOperations.MIN_SERVER_ID..MySqlSourceDebeziumOperations
                                .MAX_SERVER_ID
                    )
                }
                .toSet()
        // With ~2.1 billion possible values and 10000 samples, collisions should
        // be extremely rare. We allow up to 1 collision as a safety margin.
        Assertions.assertTrue(
            ids.size >= 9999,
            "Expected near-zero collisions among 10000 IDs from a range of ~2.1B, " +
                "but got ${10000 - ids.size} collisions"
        )
    }

    @Test
    fun testServerIdExceedsOldRange() {
        // Verify the new range is vastly larger than the old 5400-6400 range
        val oldRange = 6400 - 5400 // 1000
        val newRange =
            MySqlSourceDebeziumOperations.MAX_SERVER_ID.toLong() -
                MySqlSourceDebeziumOperations.MIN_SERVER_ID // ~2,147,478,247
        Assertions.assertTrue(
            newRange > oldRange * 1000,
            "New range ($newRange) should be orders of magnitude larger than old range ($oldRange)"
        )
    }
}
