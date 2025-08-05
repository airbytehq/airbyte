package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

interface StateKeyClient {
    fun getKey(msg: DestinationRecordRaw): StateKey

    fun acceptState(msg: CheckpointMessage)
}

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
class SelfDescribingStateKeyClient(
    private val stateWatermarkStore: StateWatermarkStore,
): StateKeyClient {
    private val ordinalMap = ConcurrentHashMap<StateKey, Long>()

    override fun getKey(msg: DestinationRecordRaw): StateKey {
        return StateKey(msg.checkpointId!!.value)
    }

    override fun acceptState(msg: CheckpointMessage) {
        val key = StateKey(msg.checkpointIdRaw!!)

        ordinalMap[key] = msg.checkpointOrdinalRaw!!.toLong()

        val inner = ConcurrentHashMap<StateKey, Long>()
        inner[key] = msg.sourceStats!!.recordCount
        val expectedCounts = StateHistogram(inner)

        stateWatermarkStore.acceptExpectedCounts(expectedCounts)
    }
}

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
class InferredStateKeyClient(
    private val stateWatermarkStore: StateWatermarkStore,
): StateKeyClient {
    private val internalCounter = AtomicLong(1)

    override fun getKey(msg: DestinationRecordRaw): StateKey {
        return StateKey(internalCounter.get().toString())
    }

    override fun acceptState(msg: CheckpointMessage) {
        val ord = internalCounter.getAndIncrement()
        val key = StateKey(ord.toString())

        val inner = ConcurrentHashMap<StateKey, Long>()
        inner[key] = msg.sourceStats!!.recordCount
        val expectedCounts = StateHistogram(inner)

        stateWatermarkStore.acceptExpectedCounts(expectedCounts)
    }
}
