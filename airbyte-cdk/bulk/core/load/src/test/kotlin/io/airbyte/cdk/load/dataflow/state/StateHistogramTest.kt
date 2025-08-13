/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import kotlin.test.assertEquals
import kotlin.test.assertNull
import org.junit.jupiter.api.Test

class StateHistogramTest {

    @Test
    fun `increment should add new key with count 1`() {
        // Given
        val histogram = StateHistogram()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        // When
        histogram.increment(stateKey)

        // Then
        assertEquals(1L, histogram.get(stateKey))
    }

    @Test
    fun `increment should increase existing key count`() {
        // Given
        val histogram = StateHistogram()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        // When
        histogram.increment(stateKey)
        histogram.increment(stateKey)
        histogram.increment(stateKey)

        // Then
        assertEquals(3L, histogram.get(stateKey))
    }

    @Test
    fun `increment should handle multiple different keys`() {
        // Given
        val histogram = StateHistogram()
        val stateKey1 = StateKey(1L, listOf(PartitionKey("partition-1")))
        val stateKey2 = StateKey(2L, listOf(PartitionKey("partition-2")))

        // When
        histogram.increment(stateKey1)
        histogram.increment(stateKey1)
        histogram.increment(stateKey2)

        // Then
        assertEquals(2L, histogram.get(stateKey1))
        assertEquals(1L, histogram.get(stateKey2))
    }

    @Test
    fun `get should return null for non-existent key`() {
        // Given
        val histogram = StateHistogram()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        // When
        val result = histogram.get(stateKey)

        // Then
        assertNull(result)
    }

    @Test
    fun `merge should combine two histograms correctly`() {
        // Given
        val histogram1 = StateHistogram()
        val histogram2 = StateHistogram()
        val stateKey1 = StateKey(1L, listOf(PartitionKey("partition-1")))
        val stateKey2 = StateKey(2L, listOf(PartitionKey("partition-2")))
        val sharedKey = StateKey(3L, listOf(PartitionKey("partition-3")))

        histogram1.increment(stateKey1)
        histogram1.increment(stateKey1)
        histogram1.increment(sharedKey)

        histogram2.increment(stateKey2)
        histogram2.increment(sharedKey)
        histogram2.increment(sharedKey)

        // When
        histogram1.merge(histogram2)

        // Then
        assertEquals(2L, histogram1.get(stateKey1))
        assertEquals(1L, histogram1.get(stateKey2))
        assertEquals(3L, histogram1.get(sharedKey)) // 1 + 2
    }

    @Test
    fun `merge should not modify the source histogram`() {
        // Given
        val histogram1 = StateHistogram()
        val histogram2 = StateHistogram()
        val stateKey1 = StateKey(1L, listOf(PartitionKey("partition-1")))
        val stateKey2 = StateKey(2L, listOf(PartitionKey("partition-2")))

        histogram1.increment(stateKey1)
        histogram2.increment(stateKey2)

        // When
        histogram1.merge(histogram2)

        // Then
        assertEquals(1L, histogram1.get(stateKey1))
        assertEquals(1L, histogram1.get(stateKey2))
        assertEquals(1L, histogram2.get(stateKey2)) // histogram2 unchanged
        assertNull(histogram2.get(stateKey1)) // histogram2 unchanged
    }

    @Test
    fun `remove should return and delete existing key`() {
        // Given
        val histogram = StateHistogram()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))
        histogram.increment(stateKey)
        histogram.increment(stateKey)

        // When
        val removedValue = histogram.remove(stateKey)

        // Then
        assertEquals(2L, removedValue)
        assertNull(histogram.get(stateKey))
    }

    @Test
    fun `remove should return null for non-existent key`() {
        // Given
        val histogram = StateHistogram()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        // When
        val removedValue = histogram.remove(stateKey)

        // Then
        assertNull(removedValue)
    }

    @Test
    fun `StateKey should be comparable by id`() {
        // Given
        val stateKey1 = StateKey(1L, listOf(PartitionKey("partition-1")))
        val stateKey2 = StateKey(2L, listOf(PartitionKey("partition-2")))
        val stateKey3 = StateKey(1L, listOf(PartitionKey("partition-3")))

        // When & Then
        assert(stateKey1 < stateKey2)
        assert(stateKey2 > stateKey1)
        assertEquals(0, stateKey1.compareTo(stateKey3))
    }
}
