/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.dataflow.state.stats.EmissionStats
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class StateHistogramStore {
    // Counts of flushed messages by partition id
    private val flushed: PartitionHistogram = PartitionHistogram(ConcurrentHashMap())
    // Counts of expected messages by state id
    private val expected: StateHistogram = StateHistogram(ConcurrentHashMap())
    // Counts of flushed bytes by partition id
    private val bytes: PartitionHistogram = PartitionHistogram(ConcurrentHashMap())

    fun acceptFlushedCounts(value: PartitionHistogram): PartitionHistogram {
        return flushed.merge(value)
    }

    fun acceptFlushedBytes(value: PartitionHistogram): PartitionHistogram {
        return bytes.merge(value)
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

    fun remove(key: StateKey): EmissionStats {
        val bytes =
            key.partitionKeys.sumOf {
                flushed.remove(it)
                bytes.remove(it) ?: 0
            }
        val count = expected.remove(key) ?: 0

        return EmissionStats(count, bytes)
    }
}
