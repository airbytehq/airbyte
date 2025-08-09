/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class StateWatermarkStore(
    val flushed: PartitionHistogram = PartitionHistogram(ConcurrentHashMap()),
    val expected: StateHistogram = StateHistogram(ConcurrentHashMap()),
) {

    fun acceptAggregateCounts(value: PartitionHistogram): PartitionHistogram {
        return flushed.merge(value)
    }

    fun acceptExpectedCounts(value: StateHistogram): StateHistogram {
        return expected.merge(value)
    }

    fun isComplete(key: StateKey): Boolean {
        val expectedCount = expected.map[key]
        val flushedCount = key.partitionIds.sumOf { flushed.map[PartitionKey(it)] ?: 0 }

        return expectedCount == flushedCount
    }
}
