/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

interface StateKeyClient {
    fun getKey(msg: DestinationRecordRaw): StateKey

    fun getOrdinal(key: StateKey): Long

    fun acceptState(msg: CheckpointMessage)
}

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
class SelfDescribingStateKeyClient(
    private val stateWatermarkStore: StateWatermarkStore,
    private val stateStore: StateStore,
) : StateKeyClient {
    private val ordinalMap = ConcurrentHashMap<StateKey, Long>()

    override fun getKey(msg: DestinationRecordRaw): StateKey {
        return StateKey(msg.checkpointId!!.value)
    }

    override fun getOrdinal(key: StateKey): Long {
        return ordinalMap[key]!!
    }

    override fun acceptState(msg: CheckpointMessage) {
        val key = StateKey(msg.checkpointIdRaw!!)
        val ordinal = msg.checkpointOrdinalRaw!!.toLong()

        ordinalMap[key] = ordinal

        val inner = ConcurrentHashMap<StateKey, Long>()
        inner[key] = msg.sourceStats!!.recordCount
        val expectedCounts = StateHistogram(inner)

        stateWatermarkStore.acceptExpectedCounts(expectedCounts)
        stateStore.accept(ordinal, msg)
    }
}

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
class InferredStateKeyClient(
    private val stateWatermarkStore: StateWatermarkStore,
    private val stateStore: StateStore,
) : StateKeyClient {
    private val internalCounter = AtomicLong(1)

    override fun getKey(msg: DestinationRecordRaw): StateKey {
        return StateKey(internalCounter.get().toString())
    }

    override fun getOrdinal(key: StateKey): Long {
        return key.id.toLong()
    }

    override fun acceptState(msg: CheckpointMessage) {
        val ordinal = internalCounter.getAndIncrement()
        val key = StateKey(ordinal.toString())

        val inner = ConcurrentHashMap<StateKey, Long>()
        inner[key] = msg.sourceStats!!.recordCount
        val expectedCounts = StateHistogram(inner)

        stateWatermarkStore.acceptExpectedCounts(expectedCounts)
        stateStore.accept(ordinal, msg)
    }
}
