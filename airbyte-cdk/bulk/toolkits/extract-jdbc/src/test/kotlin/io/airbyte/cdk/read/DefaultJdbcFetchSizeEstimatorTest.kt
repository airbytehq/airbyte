/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.read.Sample.Kind
import io.airbyte.cdk.read.TestFixtures.sharedState
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DefaultJdbcFetchSizeEstimatorTest {

    @Test
    fun testSingleSmall() {
        val sample = Sample(listOf(10L, 20L, 30L), Kind.SMALL, valueWeight = 0L)
        val sharedState = sharedState(maxMemoryBytesForTesting = 700_000, maxConcurrency = 1)
        val estimator = sharedState.jdbcFetchSizeEstimator()
        // 700_000 * 0.1 (default ratio) / 1 / 30 (max row) = 2333
        Assertions.assertEquals(2_333, estimator.apply(sample))
    }

    @Test
    fun testTwoSmall() {
        val sample = Sample(listOf(10L, 20L, 30L), Kind.SMALL, valueWeight = 0L)
        val sharedState = sharedState(maxMemoryBytesForTesting = 700_000, maxConcurrency = 2)
        val estimator = sharedState.jdbcFetchSizeEstimator()
        // 700_000 * 0.1 / 2 / 30 = 1166
        Assertions.assertEquals(1_166, estimator.apply(sample))
    }

    @Test
    fun testEmpty() {
        val sample = Sample(listOf<Long>(), Kind.EMPTY, 0L)
        val sharedState = sharedState(maxMemoryBytesForTesting = 700_000, maxConcurrency = 2)
        val estimator = sharedState.jdbcFetchSizeEstimator()
        Assertions.assertEquals(sharedState.constants.defaultFetchSize, estimator.apply(sample))
    }

    /**
     * Reproduces the failure mode from oncall#12767 / airbytehq/airbyte#69336: with a heap of
     * 8 GiB, ratio 0.3, and `maxConcurrency = 1` (source-postgres STDIO mode), the pre-fix
     * estimator would derive a per-query budget of ~2.4 GiB. When divided by a sample-derived
     * `maxRowBytes` of ~400 bytes (the wide-row tail is missed by the sample), the resulting
     * fetchSize is in the millions. The fix caps the per-query budget at
     * [DefaultJdbcConstants.MAX_MEMORY_BYTES_PER_QUERY] (500 MiB), so the fetchSize for a
     * 400-byte sampled row is bounded at 500 MiB / 400 B ≈ 1.31M rows regardless of heap.
     */
    @Test
    fun testPerQueryBufferCapAppliesWithLargeHeap() {
        // Sample row sizes mirroring the customer's `public.inbound_email_file` table:
        // 1024-row sample with max row of 403 bytes (true tail rows are much larger).
        val sample = Sample(listOf(50L, 100L, 200L, 403L), Kind.LARGE, valueWeight = 65_536L)
        val eightGiB = 8L shl 30
        // Use a permissive ratio (0.3) to force the cap branch — pre-fix this gave
        // per-query = 2.4 GiB. With the cap, per-query = 500 MiB.
        val constants = DefaultJdbcConstants(memoryCapacityRatio = 0.3)
        val sharedState =
            sharedState(
                maxMemoryBytesForTesting = eightGiB,
                maxConcurrency = 1,
                constants = constants,
            )
        val estimator = sharedState.jdbcFetchSizeEstimator()
        val perQueryCap = constants.maxMemoryBytesPerQuery // 500 MiB
        val expected = (perQueryCap / 403L).toInt()
        Assertions.assertEquals(expected, estimator.apply(sample))
        // Sanity: the unbounded computation would have been much larger.
        val unbounded = ((eightGiB * 0.3).toLong() / 403L)
        Assertions.assertTrue(unbounded > expected.toLong() * 4)
    }

    /**
     * When the heap and ratio combine to a budget smaller than the cap, the cap is a no-op and
     * the legacy formula applies. This guards against the cap being too aggressive on small
     * containers (e.g. local dev / unit tests).
     */
    @Test
    fun testPerQueryBufferCapIsNoOpOnSmallHeap() {
        val sample = Sample(listOf(10L, 20L, 30L), Kind.SMALL, valueWeight = 0L)
        val constants = DefaultJdbcConstants(memoryCapacityRatio = 0.1)
        val sharedState =
            sharedState(
                maxMemoryBytesForTesting = 700_000,
                maxConcurrency = 1,
                constants = constants,
            )
        val estimator = sharedState.jdbcFetchSizeEstimator()
        // 700_000 * 0.1 = 70_000, which is well below the 500 MiB cap. So the cap is inactive
        // and we fall back to the (budget / maxConcurrency / maxRowBytes) formula.
        // 70_000 / 1 / 30 = 2333
        Assertions.assertEquals(2_333, estimator.apply(sample))
    }

    /**
     * The cap should be respected per-query when `maxConcurrency > 1`. Even with two concurrent
     * queries on a giant heap, each query is bounded by [MAX_MEMORY_BYTES_PER_QUERY].
     */
    @Test
    fun testPerQueryBufferCapWithMultipleConcurrency() {
        val sample = Sample(listOf(100L, 1_000L), Kind.LARGE, valueWeight = 65_536L)
        val constants = DefaultJdbcConstants(memoryCapacityRatio = 0.5)
        val sharedState =
            sharedState(
                maxMemoryBytesForTesting = 16L shl 30, // 16 GiB
                maxConcurrency = 2,
                constants = constants,
            )
        val estimator = sharedState.jdbcFetchSizeEstimator()
        // Without the cap: (16 GiB * 0.5) / 2 / 1000 ≈ 4.29M rows.
        // With the cap: min(per-query-from-ratio, 500 MiB) / 1000 = 524_288 rows.
        val expected = (constants.maxMemoryBytesPerQuery / 1_000L).toInt()
        Assertions.assertEquals(expected, estimator.apply(sample))
    }
}
