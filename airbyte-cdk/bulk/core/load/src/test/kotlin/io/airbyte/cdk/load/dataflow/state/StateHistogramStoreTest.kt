/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.command.DestinationStream
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

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey, 5L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey, 1.0) }
        stateHistogramStore.acceptFlushedCounts(Fixtures.descriptor1, partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(StateScope.Global, stateKey)

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

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey, 15L) // 5 + 3 + 7 = 15

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey1, 1.0) }
        repeat(3) { partitionHistogram.increment(partitionKey2, 1.0) }
        repeat(7) { partitionHistogram.increment(partitionKey3, 1.0) }
        stateHistogramStore.acceptFlushedCounts(Fixtures.descriptor1, partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(StateScope.Global, stateKey)

        // Then
        assertTrue(result)
    }

    @Test
    fun `isComplete should return false when flushed count is less than expected count`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey, 10L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(7) { partitionHistogram.increment(partitionKey, 1.0) } // Less than expected
        stateHistogramStore.acceptFlushedCounts(Fixtures.descriptor1, partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(StateScope.Global, stateKey)

        // Then
        assertFalse(result)
    }

    @Test
    fun `isComplete should return false when flushed count is greater than expected count`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey, 5L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(8) { partitionHistogram.increment(partitionKey, 1.0) } // More than expected
        stateHistogramStore.acceptFlushedCounts(Fixtures.descriptor1, partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(StateScope.Global, stateKey)

        // Then
        assertFalse(result)
    }

    @Test
    fun `isComplete should return false when no expected count is set`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey, 1.0) }
        stateHistogramStore.acceptFlushedCounts(Fixtures.descriptor1, partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(StateScope.Global, stateKey)

        // Then
        assertFalse(result) // null != 5
    }

    @Test
    fun `isComplete should return false when no flushed counts exist`() {
        // Given
        val partitionKey = PartitionKey("partition-1")
        val stateKey = StateKey(1L, listOf(partitionKey))

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey, 5L)

        // When
        val result = stateHistogramStore.isComplete(StateScope.Global, stateKey)

        // Then
        assertFalse(result) // 5 != 0
    }

    @Test
    fun `isComplete should handle missing partition counts as zero`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2") // No flushed count for this
        val stateKey = StateKey(1L, listOf(partitionKey1, partitionKey2))

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey, 3L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(3) { partitionHistogram.increment(partitionKey1, 1.0) }
        // partitionKey2 has no flushed counts, should be treated as 0
        stateHistogramStore.acceptFlushedCounts(Fixtures.descriptor1, partitionHistogram)

        // When
        val result = stateHistogramStore.isComplete(StateScope.Global, stateKey)

        // Then
        assertTrue(result) // 3 + 0 = 3
    }

    @Test
    fun `remove should delete both expected and flushed counts for state key and return count`() {
        // Given
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2")
        val stateKey = StateKey(1L, listOf(partitionKey1, partitionKey2))
        val expectedCount = 10L
        val bytes1 = 1000L
        val bytes2 = 2000L

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey, expectedCount)

        val partitionCountsHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionCountsHistogram.increment(partitionKey1, 1.0) }
        repeat(3) { partitionCountsHistogram.increment(partitionKey2, 1.0) }
        stateHistogramStore.acceptFlushedCounts(Fixtures.descriptor1, partitionCountsHistogram)

        val partitionBytesHistogram = PartitionHistogram(ConcurrentHashMap())
        partitionBytesHistogram.increment(partitionKey1, bytes1.toDouble())
        partitionBytesHistogram.increment(partitionKey2, bytes2.toDouble())

        // When
        val count = stateHistogramStore.remove(StateScope.Global, stateKey)

        // Then
        assertEquals(expectedCount, count)
        assertFalse(
            stateHistogramStore.isComplete(StateScope.Global, stateKey)
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

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey1, 8L)
        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey2, 4L)

        val partitionHistogram = PartitionHistogram(ConcurrentHashMap())
        repeat(5) { partitionHistogram.increment(partitionKey1, 1.0) }
        repeat(3) { partitionHistogram.increment(partitionKey2, 1.0) }
        repeat(4) { partitionHistogram.increment(partitionKey3, 1.0) }
        stateHistogramStore.acceptFlushedCounts(Fixtures.descriptor1, partitionHistogram)

        // When
        stateHistogramStore.remove(StateScope.Global, stateKey1)

        // Then
        assertFalse(
            stateHistogramStore.isComplete(StateScope.Global, stateKey1)
        ) // Should be false after removal
        assertTrue(
            stateHistogramStore.isComplete(StateScope.Global, stateKey2)
        ) // Should still be complete
    }

    @Test
    fun `stream scopes should keep identical state and partition keys independent`() {
        val partitionKey = PartitionKey("abcd")
        val stateKey = StateKey(1L, listOf(partitionKey))
        val scopeA = StateScope.Stream(Fixtures.descriptor1)
        val scopeB = StateScope.Stream(Fixtures.descriptor2)

        stateHistogramStore.acceptExpectedCounts(scopeA, stateKey, 1L)
        stateHistogramStore.acceptExpectedCounts(scopeB, stateKey, 1L)
        stateHistogramStore.acceptFlushedCounts(
            Fixtures.descriptor1,
            PartitionHistogram().apply { increment(partitionKey, 1.0) },
        )
        stateHistogramStore.acceptFlushedCounts(
            Fixtures.descriptor2,
            PartitionHistogram().apply { increment(partitionKey, 1.0) },
        )

        assertTrue(stateHistogramStore.isComplete(scopeA, stateKey))
        assertTrue(stateHistogramStore.isComplete(scopeB, stateKey))

        stateHistogramStore.remove(scopeA, stateKey)

        assertFalse(stateHistogramStore.isComplete(scopeA, stateKey))
        assertTrue(stateHistogramStore.isComplete(scopeB, stateKey))
    }

    @Test
    fun `global scope should sum flushed counts across descriptors and remove all of them`() {
        val partitionKey = PartitionKey("global")
        val stateKey = StateKey(1L, listOf(partitionKey))
        val streamScope1 = StateScope.Stream(Fixtures.descriptor1)
        val streamScope2 = StateScope.Stream(Fixtures.descriptor2)

        stateHistogramStore.acceptExpectedCounts(StateScope.Global, stateKey, 2L)
        stateHistogramStore.acceptExpectedCounts(streamScope1, stateKey, 1L)
        stateHistogramStore.acceptExpectedCounts(streamScope2, stateKey, 1L)
        stateHistogramStore.acceptFlushedCounts(
            Fixtures.descriptor1,
            PartitionHistogram().apply { increment(partitionKey, 1.0) },
        )
        stateHistogramStore.acceptFlushedCounts(
            Fixtures.descriptor2,
            PartitionHistogram().apply { increment(partitionKey, 1.0) },
        )

        assertTrue(stateHistogramStore.isComplete(StateScope.Global, stateKey))
        stateHistogramStore.remove(StateScope.Global, stateKey)
        assertFalse(stateHistogramStore.isComplete(StateScope.Global, stateKey))
        assertFalse(stateHistogramStore.isComplete(streamScope1, stateKey))
        assertFalse(stateHistogramStore.isComplete(streamScope2, stateKey))
    }

    private object Fixtures {
        val descriptor1 = DestinationStream.Descriptor("ns", "stream1")
        val descriptor2 = DestinationStream.Descriptor("ns", "stream2")
    }
}
