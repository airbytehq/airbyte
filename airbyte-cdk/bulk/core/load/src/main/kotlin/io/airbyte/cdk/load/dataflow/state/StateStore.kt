/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentSkipListMap

@Singleton
class StateStore(
    private val stateClient: StateKeyClient,
) {
    // Counts of flushed messages by partition id
    private val flushed: PartitionHistogram = PartitionHistogram(ConcurrentHashMap())
    // Counts of expected messages by state id
    private val expected: StateHistogram = StateHistogram(ConcurrentHashMap())
    // state messages ordered by ID
    private val states = ConcurrentSkipListMap<StateKey, CheckpointMessage>()

    fun accept(msg: CheckpointMessage) {
        val key = stateClient.getStateKey(msg)
        acceptExpectedCounts(key, msg.sourceStats!!.recordCount)
        states[key] = msg
    }

    fun remove(key: StateKey): CheckpointMessage = states.remove(key)!!

    fun acceptFlushedCounts(value: PartitionHistogram): PartitionHistogram {
        return flushed.merge(value)
    }

    fun acceptExpectedCounts(key: StateKey, count: Long): StateHistogram {
        val inner = ConcurrentHashMap<StateKey, Long>()
        inner[key] = count

        return expected.merge(StateHistogram(inner))
    }

    fun getNextComplete(): CheckpointMessage? {
        if (states.isEmpty()) return null

        val key = states.firstKey()
        if (!isComplete(key)) return null

        return states.remove(key)
    }

    fun isComplete(key: StateKey): Boolean {
        val expectedCount = expected.map[key]
        val flushedCount = key.partitionIds.sumOf { flushed.map[PartitionKey(it)] ?: 0 }

        return expectedCount == flushedCount
    }
}
