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

interface StateClient {
    fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey

    fun acceptState(msg: CheckpointMessage)
}

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
class SelfDescribingStateKeyClient(
    private val stateWatermarkStore: StateWatermarkStore,
    private val stateStore: StateStore,
) : StateClient {
    override fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey {
        return PartitionKey(msg.checkpointId!!.value)
    }

    override fun acceptState(msg: CheckpointMessage) {
        val ordinal = msg.checkpointOrdinalRaw!!.toLong()
        val key = StateKey(ordinal, msg.checkpointPartitionIds)

        val inner = ConcurrentHashMap<StateKey, Long>()
        inner[key] = msg.sourceStats!!.recordCount
        val expectedCounts = StateHistogram(inner)

        stateWatermarkStore.acceptExpectedCounts(expectedCounts)
        stateStore.accept(key, msg)
    }
}

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
class InferredStateKeyClient(
    private val stateWatermarkStore: StateWatermarkStore,
    private val stateStore: StateStore,
) : StateClient {
    private val internalCounter = AtomicLong(1)

    override fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey {
        return PartitionKey(internalCounter.get().toString())
    }

    override fun acceptState(msg: CheckpointMessage) {
        val ordinal = internalCounter.getAndIncrement()
        val key = StateKey(ordinal, listOf(ordinal.toString()))

        val inner = ConcurrentHashMap<StateKey, Long>()
        inner[key] = msg.sourceStats!!.recordCount
        val expectedCounts = StateHistogram(inner)

        stateWatermarkStore.acceptExpectedCounts(expectedCounts)
        stateStore.accept(key, msg)
    }
}
