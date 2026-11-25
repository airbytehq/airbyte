/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConcurrentPartitionsCreator.Companion.computeNumPartitions
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * The partition count of a concurrent snapshot is `ceil(table size / target partition size)`,
 * clamped to `[1, max-partitions]`. It is independent of the sample size, so a multi-terabyte table
 * is no longer limited to 1024 partitions.
 */
class PostgresSourceJdbcPartitionsCreatorTest {

    private val mib = 1L shl 20
    private val tib = 1L shl 40

    @Test
    fun `a table no larger than the target is one partition`() {
        assertEquals(1, computeNumPartitions(100 * mib, 750 * mib, DEFAULT_MAX_PARTITIONS))
        assertEquals(1, computeNumPartitions(750 * mib, 750 * mib, DEFAULT_MAX_PARTITIONS))
    }

    @Test
    fun `the count is the table size over the target, rounded up`() {
        assertEquals(2, computeNumPartitions(750 * mib + 1, 750 * mib, DEFAULT_MAX_PARTITIONS))
        assertEquals(4, computeNumPartitions(3000 * mib, 750 * mib, DEFAULT_MAX_PARTITIONS))
        assertEquals(5, computeNumPartitions(3001 * mib, 750 * mib, DEFAULT_MAX_PARTITIONS))
    }

    @Test
    fun `a multi-terabyte table exceeds the former sample-size cap`() {
        // 4 TiB at the default target of 4 concurrent readers (750 MiB each).
        val numPartitions = computeNumPartitions(4 * tib, 750 * mib, DEFAULT_MAX_PARTITIONS)
        assertEquals(5593, numPartitions)
    }

    @Test
    fun `the count is capped at max-partitions`() {
        assertEquals(
            DEFAULT_MAX_PARTITIONS,
            computeNumPartitions(4 * tib, 100 * mib, DEFAULT_MAX_PARTITIONS),
        )
        assertEquals(2048, computeNumPartitions(4 * tib, 100 * mib, 2048))
    }

    @Test
    fun `degenerate inputs fall back to one partition`() {
        assertEquals(1, computeNumPartitions(0, 750 * mib, DEFAULT_MAX_PARTITIONS))
        assertEquals(1, computeNumPartitions(-1, 750 * mib, DEFAULT_MAX_PARTITIONS))
        assertEquals(1, computeNumPartitions(4 * tib, 0, DEFAULT_MAX_PARTITIONS))
        assertEquals(1, computeNumPartitions(4 * tib, 750 * mib, 1))
        assertEquals(1, computeNumPartitions(4 * tib, 750 * mib, 0))
    }
}
