/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import java.util.concurrent.ConcurrentHashMap
import kotlin.test.assertEquals
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
        repeat(5) { partitionHistogram.increment(partitionKey, 1) }
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
        repeat(5) { partitionHistogram.increment(partitionKey1, 1) }
        repeat(3) { partitionHistogram.increment(partitionKey2, 1) }
        repeat(7) { partitionHistogram.increment(partitionKey3, 1) }
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
        repeat(7) { partitionHistogram.increment(partitionKey, 1) } // Less than expected
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
        repeat(8) { partitionHistogram.increment(partitionKey, 1) } // More than expected
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
        repeat(5) { partitionHistogram.increment(partitionKey, 1) }
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
        repeat(3) { partitionHistogram.increment(partitionKey1, 1) }
        // partitionKey2 has no flushed counts, should be treated as 0
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(stateKey)

        // Then
        assertTrue(result) // 3 + 0 = 3
    }

    @Test
    fun `remove should delete both expected and flushed counts for state key and return stats`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2")
        val stateKey = StateKey(1L, listOf(partitionKey1, partitionKey2))
        val expectedCount = 10L
        val bytes1 = 1000L
        val bytes2 = 2000L

        stateHistogramStore.acceptExpectedCounts(stateKey, expectedCount)

        val partitionCountsHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionCountsHistogram.increment(partitionKey1, 1) }
        repeat(3) { partitionCountsHistogram.increment(partitionKey2, 1) }
        stateHistogramStore.acceptFlushedCounts(partitionCountsHistogram)

        val partitionBytesHistogram = PartitionHistogram(ConcurrentHashMap())
        partitionBytesHistogram.increment(partitionKey1, bytes1)
        partitionBytesHistogram.increment(partitionKey2, bytes2)
        stateHistogramStore.acceptFlushedBytes(partitionBytesHistogram)

        // When
        val stats = stateHistogramStore.remove(stateKey)

        // Then
        assertEquals(expectedCount, stats.count)
        assertEquals(bytes1 + bytes2, stats.bytes)
        assertFalse(
            stateHistogramStore.isComplete(stateKey)
        ) // Should be false due to missing expected count
    }

    @Test
    fun `remove should handle missing byte counts as zero`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))
        val expectedCount = 5L

        stateHistogramStore.acceptExpectedCounts(stateKey, expectedCount)

        val partitionCountsHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionCountsHistogram.increment(partitionKey, 1) }
        stateHistogramStore.acceptFlushedCounts(partitionCountsHistogram)

        // No bytes histogram added - should be treated as 0

        // When
        val stats = stateHistogramStore.remove(stateKey)

        // Then
        assertEquals(expectedCount, stats.count)
        assertEquals(0L, stats.bytes) // No bytes were added
    }

    @Test
    fun `remove should sum bytes from multiple partitions correctly`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2")
        val partitionKey3 = PartitionKey("partition-3")
        val stateKey = StateKey(1L, listOf(partitionKey1, partitionKey2, partitionKey3))
        val expectedCount = 15L
        val bytes1 = 5000L
        val bytes2 = 3000L
        val bytes3 = 7000L

        stateHistogramStore.acceptExpectedCounts(stateKey, expectedCount)

        val partitionCountsHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(7) { partitionCountsHistogram.increment(partitionKey1, 1) }
        repeat(3) { partitionCountsHistogram.increment(partitionKey2, 1) }
        repeat(5) { partitionCountsHistogram.increment(partitionKey3, 1) }
        stateHistogramStore.acceptFlushedCounts(partitionCountsHistogram)

        val partitionBytesHistogram = PartitionHistogram(ConcurrentHashMap())
        partitionBytesHistogram.increment(partitionKey1, bytes1)
        partitionBytesHistogram.increment(partitionKey2, bytes2)
        partitionBytesHistogram.increment(partitionKey3, bytes3)
        stateHistogramStore.acceptFlushedBytes(partitionBytesHistogram)

        // When
        val stats = stateHistogramStore.remove(stateKey)

        // Then
        assertEquals(expectedCount, stats.count)
        assertEquals(bytes1 + bytes2 + bytes3, stats.bytes)
    }

    @Test
    fun `remove should handle partial byte counts for partitions`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2")
        val stateKey = StateKey(1L, listOf(partitionKey1, partitionKey2))
        val expectedCount = 10L
        val bytes1 = 2500L
        // partitionKey2 will have no bytes recorded

        stateHistogramStore.acceptExpectedCounts(stateKey, expectedCount)

        val partitionCountsHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(6) { partitionCountsHistogram.increment(partitionKey1, 1) }
        repeat(4) { partitionCountsHistogram.increment(partitionKey2, 1) }
        stateHistogramStore.acceptFlushedCounts(partitionCountsHistogram)

        val partitionBytesHistogram = PartitionHistogram(ConcurrentHashMap())
        partitionBytesHistogram.increment(partitionKey1, bytes1)
        // No bytes for partitionKey2
        stateHistogramStore.acceptFlushedBytes(partitionBytesHistogram)

        // When
        val stats = stateHistogramStore.remove(stateKey)

        // Then
        assertEquals(expectedCount, stats.count)
        assertEquals(bytes1, stats.bytes) // Only bytes from partition1
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
        repeat(5) { partitionHistogram.increment(partitionKey1, 1) }
        repeat(3) { partitionHistogram.increment(partitionKey2, 1) }
        repeat(4) { partitionHistogram.increment(partitionKey3, 1) }
        stateHistogramStore.acceptFlushedCounts(partitionHistogram)

        // When
        stateHistogramStore.remove(stateKey1)

        // Then
        assertFalse(stateHistogramStore.isComplete(stateKey1)) // Should be false after removal
        assertTrue(stateHistogramStore.isComplete(stateKey2)) // Should still be complete
    }
}
