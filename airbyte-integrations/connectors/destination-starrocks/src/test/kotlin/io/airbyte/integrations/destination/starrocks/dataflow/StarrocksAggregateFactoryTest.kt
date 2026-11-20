/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.dataflow

import io.airbyte.integrations.destination.starrocks.write.load.CsvRowInsertBuffer
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Guards the `__op` collision check that prevents a corrupt CDC load: the Stream Load delete/upsert
 * path appends an `__op` column, so a source column of the same name must be rejected — but only on
 * the Stream Load path, since the SQL load path (INSERT/DELETE) never adds `__op` (#45, #68).
 */
class StarrocksAggregateFactoryTest {

    private val op = CsvRowInsertBuffer.OP_COLUMN // "__op"

    @Test
    fun `collides when a CDC-delete Stream Load stream has an __op column`() {
        assertTrue(
            StarrocksAggregateFactory.opColumnCollides(
                cdcDelete = true,
                loadAsSql = false,
                finalColumnNames = setOf("id", op),
            ),
        )
    }

    @Test
    fun `no collision on the SQL load path (INSERT-DELETE, no __op column appended)`() {
        assertFalse(
            StarrocksAggregateFactory.opColumnCollides(
                cdcDelete = true,
                loadAsSql = true,
                finalColumnNames = setOf("id", op),
            ),
        )
    }

    @Test
    fun `no collision without a CDC hard-delete`() {
        assertFalse(
            StarrocksAggregateFactory.opColumnCollides(
                cdcDelete = false,
                loadAsSql = false,
                finalColumnNames = setOf("id", op),
            ),
        )
    }

    @Test
    fun `no collision when no column is named __op`() {
        assertFalse(
            StarrocksAggregateFactory.opColumnCollides(
                cdcDelete = true,
                loadAsSql = false,
                finalColumnNames = setOf("id", "name"),
            ),
        )
    }
}
