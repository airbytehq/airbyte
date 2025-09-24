/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.lang.IllegalStateException
import java.util.concurrent.ConcurrentHashMap
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
class InferredStateKeyClient(
    private val catalog: DestinationCatalog,
) : StateKeyClient {
    private val globalSequence = AtomicLong(1)
    private var streamCounters = ConcurrentHashMap<DestinationStream.Descriptor, AtomicLong>()

    override fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey {
        val desc = msg.stream.unmappedDescriptor
        val streamOrdinal = streamCounters.computeIfAbsent(desc) { AtomicLong(1) }
        return PartitionKey("${desc.namespace}-${desc.name}-$streamOrdinal")
    }

    override fun getStateKey(msg: CheckpointMessage): StateKey {
        val ordinal = globalSequence.getAndIncrement()

        when (msg) {
            is StreamCheckpoint -> {
                val desc = msg.checkpoint.unmappedDescriptor
                val counter = streamCounters.computeIfAbsent(desc) { AtomicLong(1) }
                val streamOrdinal = counter.getAndIncrement()

                val partitions = listOf(
                    PartitionKey("${desc.namespace}-${desc.name}-$streamOrdinal"),
                )
                return StateKey(ordinal, partitions)
            }

            is GlobalCheckpoint,
            is GlobalSnapshotCheckpoint -> {
                val partitions = msg.checkpoints.map {
                    val desc = it.unmappedDescriptor
                    val counter = streamCounters.computeIfAbsent(desc) { AtomicLong(1) }
                    val streamOrdinal = counter.getAndIncrement()
                    PartitionKey("${desc.namespace}-${desc.name}-$streamOrdinal")
                }

                return StateKey(ordinal, partitions)
            }
        }
    }
}
