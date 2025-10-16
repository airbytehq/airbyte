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

    fun acceptFlushedCounts(value: PartitionHistogram): PartitionHistogram {
        return flushed.merge(value)
    }

    fun acceptExpectedCounts(key: StateKey, count: Long): StateHistogram {
        val inner = ConcurrentHashMap<StateKey, Long>()
        inner[key] = count

        return expected.merge(StateHistogram(inner))
    }

    fun isComplete(key: StateKey): Boolean {
        val expectedCount = expected.get(key)
        val flushedCount = key.partitionKeys.sumOf { flushed.get(it) ?: 0 }

        return expectedCount == flushedCount
    }

    fun remove(key: StateKey): Long? {
        key.partitionKeys.forEach { flushed.remove(it) }
        return expected.remove(key)
    }
}
