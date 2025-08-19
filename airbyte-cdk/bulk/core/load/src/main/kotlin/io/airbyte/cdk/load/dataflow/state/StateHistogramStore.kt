/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class StateHistogramStore {
    // Counts of flushed messages by partition id
    private val flushed: PartitionHistogram = PartitionHistogram(ConcurrentHashMap())
    // Counts of expected messages by state id
    private val expected: StateHistogram = StateHistogram(ConcurrentHashMap())
    // Counts of expected messages size by state id
    private val expectedSize: StateHistogram = StateHistogram(ConcurrentHashMap())

    fun acceptFlushedCounts(value: PartitionHistogram): PartitionHistogram {
        return flushed.merge(value)
    }

    fun acceptExpectedCountsAndSize(key: StateKey, count: Long, size: Long): StateHistogram {
        val innerCount = ConcurrentHashMap<StateKey, Long>()
        innerCount[key] = count

        val innerSize = ConcurrentHashMap<StateKey, Long>()
        innerSize[key] = size


        return expected.merge(StateHistogram(innerCount))
    }

    fun isComplete(key: StateKey): Boolean {
        val expectedCount = expected.get(key)
        val flushedCount = key.partitionKeys.sumOf { flushed.get(it) ?: 0 }

        return expectedCount == flushedCount
    }

    fun remove(key: StateKey) {
        expected.remove(key)
        key.partitionKeys.forEach { flushed.remove(it) }
    }

    fun get(key: StateKey) = expected.get(key)
}
