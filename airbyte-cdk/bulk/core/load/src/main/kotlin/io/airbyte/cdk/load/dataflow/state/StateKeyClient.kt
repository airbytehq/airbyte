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
class SelfDescribingStateKeyClient: StateKeyClient {
    private val ordinalMap = ConcurrentHashMap<StateKey, Long>()

    override fun getKey(msg: DestinationRecordRaw): StateKey {
        return StateKey(msg.checkpointId!!.value)
    }

    override fun acceptState(msg: CheckpointMessage) {
        val key = StateKey(msg.checkpointIdRaw!!)

        ordinalMap[key] = msg.checkpointOrdinalRaw!!.toLong()
    }
}

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
class InferredStateKeyClient: StateKeyClient {
    private val internalCounter = AtomicLong(1)

    override fun getKey(msg: DestinationRecordRaw): StateKey {
        return StateKey(internalCounter.get().toString())
    }

    override fun acceptState(msg: CheckpointMessage) {
        internalCounter.getAndIncrement()
    }
}
