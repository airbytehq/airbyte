/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.dataflow.state.stats.StateStatsEnricher
import io.airbyte.cdk.load.message.CheckpointMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentSkipListMap
import java.util.concurrent.atomic.AtomicLong

@Singleton
class StateStore(
    private val keyClient: StateKeyClient,
    private val histogramStore: StateHistogramStore,
    private val stateStatsEnricher: StateStatsEnricher,
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
        histogramStore.remove(key)
        val msg = states.remove(key)!!

        return stateStatsEnricher.enrich(msg, key)
    }

    fun hasStates(): Boolean = states.isNotEmpty()

    /** Log some information about why state messages cannot be flushed. */
    // implementation-wise, this is largely just mirroring getNextComplete(),
    // except it logs things instead of actually doing anything.
    fun logStateInfo() {
        val message = StringBuilder("State diagnostic information:")
        val key = states.firstKey()
        val state = states.get(key)
        message.append("\nFirst state key: $key (full state message: $state)")
        if (key.id != stateSequence.get()) {
            message.append("\nKey ID did not match state sequence ($stateSequence.get()")
        } else if (!histogramStore.isComplete(key)) {
            message.append(
                "\nhistogram store says key is incomplete: ${histogramStore.whyIsStateIncomplete(key)}"
            )
        }
        log.info { message }
        return
    }
}
