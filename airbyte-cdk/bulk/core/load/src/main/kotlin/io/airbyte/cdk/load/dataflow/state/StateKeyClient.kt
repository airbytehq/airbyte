/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicLong

interface StateKeyClient {
    fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey

    fun getStateKey(msg: CheckpointMessage): StateKey
}

/**
 * Calculates state / partition keys based off the incoming State message. States and Partitions may
 * be either 1 to 1 or 1 to many.
 *
 * Only for use for multithreaded "speed-mode" input streams. Source must specify partition / id on
 * the State message.
 */
@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
class SelfDescribingStateKeyClient : StateKeyClient {
    override fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey {
        return PartitionKey(msg.checkpointId!!.value)
    }

    override fun getStateKey(msg: CheckpointMessage): StateKey {
        val ordinal = msg.checkpointOrdinalRaw!!.toLong()
        val partitions = msg.checkpointPartitionIds.map { PartitionKey(it) }
        return StateKey(ordinal, partitions)
    }
}

/**
 * Calculates state / partition keys based off a global counter. States are Partitions are 1 to 1.
 *
 * Only for use for single threaded input streams.
 */
@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
class InferredStateKeyClient : StateKeyClient {
    private val internalCounter = AtomicLong(1)

    override fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey {
        return PartitionKey(internalCounter.get().toString())
    }

    override fun getStateKey(msg: CheckpointMessage): StateKey {
        val ordinal = internalCounter.getAndIncrement()
        val partitions = listOf(PartitionKey(ordinal.toString()))
        return StateKey(ordinal, partitions)
    }
}
