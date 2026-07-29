/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.command.DestinationStream
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class StateHistogramStore {
    // Counts of flushed messages by mapped stream descriptor and partition id.
    private val flushed = ConcurrentHashMap<DestinationStream.Descriptor, PartitionHistogram>()
    // Counts of expected messages by scope and state id.
    private val expected = ConcurrentHashMap<StateScope, StateHistogram>()

    fun acceptFlushedCounts(
        descriptor: DestinationStream.Descriptor,
        value: PartitionHistogram,
    ): PartitionHistogram {
        return flushed
            .computeIfAbsent(descriptor) { PartitionHistogram(ConcurrentHashMap()) }
            .merge(value)
    }

    fun acceptExpectedCounts(scope: StateScope, key: StateKey, count: Long): StateHistogram {
        val inner = ConcurrentHashMap<StateKey, Double>()
        inner[key] = count.toDouble()

        return expected
            .computeIfAbsent(scope) { StateHistogram(ConcurrentHashMap()) }
            .merge(StateHistogram(inner))
    }

    fun isComplete(scope: StateScope, key: StateKey): Boolean {
        val expectedCount = expected[scope]?.get(key)
        val flushedCount = flushedCount(scope, key)

        return expectedCount == flushedCount
    }

    // mirrors isComplete. Purely for debugging purposes.
    fun whyIsStateIncomplete(scope: StateScope, key: StateKey): String {
        val expectedCount = expected[scope]?.get(key)
        val partitionFlushCounts =
            key.partitionKeys.map { partitionKey ->
                when (scope) {
                    StateScope.Global -> flushed.values.sumOf { it.get(partitionKey) ?: 0.0 }
                    is StateScope.Stream -> flushed[scope.descriptor]?.get(partitionKey) ?: 0.0
                }
            }
        val flushedCount = partitionFlushCounts.sum()
        return "scope $scope: expectedCount $expectedCount does not equal flushedCount $flushedCount (by partition: $partitionFlushCounts)"
    }

    fun remove(scope: StateScope, key: StateKey): Long? {
        when (scope) {
            StateScope.Global ->
                flushed.values.forEach { histogram ->
                    key.partitionKeys.forEach { histogram.remove(it) }
                }
            is StateScope.Stream ->
                flushed[scope.descriptor]?.let { histogram ->
                    key.partitionKeys.forEach { histogram.remove(it) }
                }
        }
        return expected[scope]?.remove(key)?.toLong()
    }

    private fun flushedCount(scope: StateScope, key: StateKey): Double =
        key.partitionKeys.sumOf { partitionKey ->
            when (scope) {
                StateScope.Global -> flushed.values.sumOf { it.get(partitionKey) ?: 0.0 }
                is StateScope.Stream -> flushed[scope.descriptor]?.get(partitionKey) ?: 0.0
            }
        }
}
