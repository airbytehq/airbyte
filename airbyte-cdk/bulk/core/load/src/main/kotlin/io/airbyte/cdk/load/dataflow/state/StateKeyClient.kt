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
 * Calculates state / partition keys based off per stream counters. For per-stream state, partitions
 * are 1:1 with state messages. For global states, each state has a partition for each stream.
 *
 * Only for use for single threaded input streams.
 */
@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
class InferredStateKeyClient(private val catalog: DestinationCatalog) : StateKeyClient {
    // sequence of all state messages
    private val globalCounter = AtomicLong(1)

    // sequence of state messages per stream
    private var streamCounters = ConcurrentHashMap<DestinationStream.Descriptor, AtomicLong>()

    // caches keys / strings for perf reasons
    private val keyCache = ConcurrentHashMap<DestinationStream.Descriptor, PartitionKey>()

    override fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey =
        getCachedKeyForDesc(msg.stream.unmappedDescriptor)

    override fun getStateKey(msg: CheckpointMessage): StateKey {
        val ordinal = globalCounter.getAndIncrement()

        when (msg) {
            is StreamCheckpoint -> {
                val partitions = listOf(getCachedKeyForDesc(msg.checkpoint.unmappedDescriptor))
                incrementForDesc(msg.checkpoint.unmappedDescriptor)
                return StateKey(ordinal, partitions)
            }
            is GlobalCheckpoint,
            is GlobalSnapshotCheckpoint -> {
                val partitions =
                    catalog.streams.map {
                        val key = getCachedKeyForDesc(it.unmappedDescriptor)
                        incrementForDesc(it.unmappedDescriptor)
                        key
                    }
                return StateKey(ordinal, partitions)
            }
        }
    }

    private fun getCachedKeyForDesc(desc: DestinationStream.Descriptor) =
        keyCache.computeIfAbsent(desc, this::partitionKeyForDesc)

    private fun incrementForDesc(desc: DestinationStream.Descriptor) {
        val counter = streamCounters.computeIfAbsent(desc) { AtomicLong(1) }
        counter.getAndIncrement()
        keyCache[desc] = partitionKeyForDesc(desc)
    }

    private fun partitionKeyForDesc(desc: DestinationStream.Descriptor): PartitionKey {
        val counter = streamCounters.computeIfAbsent(desc) { AtomicLong(1) }
        val streamOrdinal = counter.get()
        return if (desc.namespace == null) {
            PartitionKey("${desc.name}-$streamOrdinal")
        } else {
            PartitionKey("${desc.namespace}-${desc.name}-$streamOrdinal")
        }
    }
}
