package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentSkipListMap
import java.util.concurrent.atomic.AtomicLong

@Singleton
class StateStore {
    private val watermark = AtomicLong()
    val states = ConcurrentSkipListMap<Long, CheckpointMessage>()

    fun accept(ordinal: Long, msg: CheckpointMessage) {
        states[ordinal] = msg
    }

    fun remove(ordinal: Long): CheckpointMessage = states.remove(ordinal)!!

    fun getAll(): List<CheckpointMessage> = states.values.toList()
}
