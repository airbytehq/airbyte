/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import java.util.concurrent.ConcurrentHashMap
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class StateHistogramStoreTest {

    private lateinit var stateHistogramStore: StateHistogramStore

    @BeforeEach
    fun setUp() {
        stateHistogramStore = StateHistogramStore()
    }

    @Test
    fun `isComplete should return true when flushed count equals expected count for single partition`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        stateHistogramStore.acceptExpectedCounts(stateKey, 5L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey) }
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(stateKey)

        // Then
        assertTrue(result)
    }

    @Test
    fun `isComplete should return true when flushed count equals expected count for multiple partitions`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2")
        val partitionKey3 = PartitionKey("partition-3")
        val stateKey = StateKey(1L, listOf(partitionKey1, partitionKey2, partitionKey3))

        stateHistogramStore.acceptExpectedCounts(stateKey, 15L) // 5 + 3 + 7 = 15

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey1) }
        repeat(3) { partitionHistogram.increment(partitionKey2) }
        repeat(7) { partitionHistogram.increment(partitionKey3) }
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(stateKey)

        // Then
        assertTrue(result)
    }

    @Test
    fun `isComplete should return false when flushed count is less than expected count`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        stateHistogramStore.acceptExpectedCounts(stateKey, 10L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(7) { partitionHistogram.increment(partitionKey) } // Less than expected
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(stateKey)

        // Then
        assertFalse(result)
    }

    @Test
    fun `isComplete should return false when flushed count is greater than expected count`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        stateHistogramStore.acceptExpectedCounts(stateKey, 5L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(8) { partitionHistogram.increment(partitionKey) } // More than expected
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(stateKey)

        // Then
        assertFalse(result)
    }

    @Test
    fun `isComplete should return false when no expected count is set`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey) }
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(stateKey)

        // Then
        assertFalse(result) // null != 5
    }

    @Test
    fun `isComplete should return false when no flushed counts exist`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        stateHistogramStore.acceptExpectedCounts(stateKey, 5L)

        // When
        val result = stateHistogramStore.isComplete(stateKey)

        // Then
        assertFalse(result) // 5 != 0
    }

    @Test
    fun `isComplete should handle missing partition counts as zero`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2") // No flushed count for this
        val stateKey = StateKey(1L, listOf(partitionKey1, partitionKey2))

        stateHistogramStore.acceptExpectedCounts(stateKey, 3L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(3) { partitionHistogram.increment(partitionKey1) }
        // partitionKey2 has no flushed counts, should be treated as 0
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(stateKey)

        // Then
        assertTrue(result) // 3 + 0 = 3
    }

    @Test
    fun `remove should delete both expected and flushed counts for state key`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2")
        val stateKey = StateKey(1L, listOf(partitionKey1, partitionKey2))

        stateHistogramStore.acceptExpectedCounts(stateKey, 10L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey1) }
        repeat(3) { partitionHistogram.increment(partitionKey2) }
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        stateHistogramStore.remove(stateKey)

        // Then
        assertFalse(
            stateHistogramStore.isComplete(stateKey)
        ) // Should be false due to missing expected count
    }

    @Test
    fun `remove should only affect specified state key and partitions`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2")
        val partitionKey3 = PartitionKey("partition-3")

        val stateKey1 = StateKey(1L, listOf(partitionKey1, partitionKey2))
        val stateKey2 = StateKey(2L, listOf(partitionKey3))

        stateHistogramStore.acceptExpectedCounts(stateKey1, 8L)
        stateHistogramStore.acceptExpectedCounts(stateKey2, 4L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey1) }
        repeat(3) { partitionHistogram.increment(partitionKey2) }
        repeat(4) { partitionHistogram.increment(partitionKey3) }
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        stateHistogramStore.remove(stateKey1)

        // Then
        assertFalse(stateHistogramStore.isComplete(stateKey1)) // Should be false after removal
        assertTrue(stateHistogramStore.isComplete(stateKey2)) // Should still be complete
    }
}
