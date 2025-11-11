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
class InferredStateKeyClient(
    private val catalog: DestinationCatalog,
) : StateKeyClient {

    private val counters = ConcurrentHashMap<DestinationStream.Descriptor, AtomicLong>()

    private val keyCache = ConcurrentHashMap<DestinationStream.Descriptor, PartitionKey>()

    override fun getPartitionKey(msg: DestinationRecordRaw): PartitionKey =
        currentKey(msg.stream.unmappedDescriptor)

    override fun getStateKey(msg: CheckpointMessage): StateKey =
        when (msg) {
            is StreamCheckpoint -> {
                val desc = msg.checkpoint.unmappedDescriptor

                val ordinal = currentOrdinal(desc)
                val partitions = listOf(currentKey(desc))
                advance(desc)
                StateKey(ordinal, partitions)
            }
            is GlobalCheckpoint,
            is GlobalSnapshotCheckpoint -> {
                val streams = catalog.streams
                require(streams.isNotEmpty()) {
                    "Catalog contains no streams; cannot emit global state."
                }

                val ordinals =
                    streams.map { it.unmappedDescriptor to currentOrdinal(it.unmappedDescriptor) }
                val universal = ordinals.first().second
                check(ordinals.all { it.second == universal }) {
                    "For global state, all streams must share the same ordinal. Found=${ordinals.map { it.second }.toSet()}."
                }

                val partitions = streams.map { currentKey(it.unmappedDescriptor) }
                streams.forEach { advance(it.unmappedDescriptor) }

                StateKey(universal, partitions)
            }
        }

    private fun counter(desc: DestinationStream.Descriptor): AtomicLong =
        counters.computeIfAbsent(desc) { AtomicLong(1L) }

    private fun currentOrdinal(desc: DestinationStream.Descriptor): Long = counter(desc).get()

    private fun currentKey(desc: DestinationStream.Descriptor): PartitionKey =
        keyCache.computeIfAbsent(desc) { keyFor(desc, currentOrdinal(desc)) }

    private fun advance(desc: DestinationStream.Descriptor) {
        val next = counter(desc).incrementAndGet()
        keyCache[desc] = keyFor(desc, next)
    }

    private fun keyFor(desc: DestinationStream.Descriptor, ordinal: Long): PartitionKey {
        val base =
            if (desc.namespace.isNullOrEmpty()) desc.name else "${desc.namespace}-${desc.name}"
        return PartitionKey("$base-$ordinal")
    }
}
