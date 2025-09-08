/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentSkipListMap
import java.util.concurrent.atomic.AtomicLong

@Singleton
class StateStore(
    private val keyClient: StateKeyClient,
    private val histogramStore: StateHistogramStore,
) {
    private val log = KotlinLogging.logger {}

    // state messages ordered by ID
    private val states = ConcurrentSkipListMap<StateKey, CheckpointMessage>()
    // we publish states sequentially starting from 1
    private val stateSequence = AtomicLong(1)

    fun accept(msg: CheckpointMessage) {
        val key = keyClient.getStateKey(msg)
        histogramStore.acceptExpectedCounts(key, msg.sourceStats!!.recordCount)
        states[key] = msg
    }

    fun remove(key: StateKey): CheckpointMessage = states.remove(key)!!

    fun getNextComplete(): CheckpointMessage? {
        if (states.isEmpty()) return null

        val key = states.firstKey()
        if (key.id != stateSequence.get()) return null
        if (!histogramStore.isComplete(key)) return null

        stateSequence.incrementAndGet()
        val msg = states.remove(key)
        val count = histogramStore.remove(key)!!

        // Add count to stats (will always equal source stats)
        // TODO: decide what we want to do with dest stats
        msg!!.updateStats(
            destinationStats = CheckpointMessage.Stats(count),
            totalRecords = count,
        )

        return msg
    }

    fun hasStates(): Boolean = states.isNotEmpty()
}
