/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.CloseableCoroutine
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.merge

interface PartitionedQueue<T> : CloseableCoroutine {
    val partitions: Int
    fun consume(partition: Int): Flow<T>
    suspend fun publish(value: T, partition: Int)
    suspend fun broadcast(value: T)
}

class StrictPartitionedQueue<T>(private val queues: Array<MessageQueue<T>>) : PartitionedQueue<T> {
    override val partitions = queues.size

    override fun consume(partition: Int): Flow<T> {
        if (partition < 0 || partition >= partitions) {
            throw IllegalArgumentException("Invalid partition: $partition")
        }
        return queues[partition].consume()
    }

    override suspend fun publish(value: T, partition: Int) {
        if (partition < 0 || partition >= partitions) {
            throw IllegalArgumentException("Invalid partition: $partition")
        }
        queues[partition].publish(value)
    }

    override suspend fun broadcast(value: T) = queues.forEach { it.publish(value) }

    override suspend fun close() {
        queues.forEach { it.close() }
    }
}

/**
 * This is for the use case where you want workers to grab work as it becomes available but still be
 * able to receive notifications that are guaranteed to be consumed by every partition.
 */
class SinglePartitionQueueWithMultiPartitionBroadcast<T>(
    private val sharedQueue: MessageQueue<T>,
    override val partitions: Int
) : PartitionedQueue<T> {
    private val broadcastChannels =
        StrictPartitionedQueue(
            (0 until partitions).map { ChannelMessageQueue<T>(Channel(1)) }.toTypedArray()
        )

    override fun consume(partition: Int): Flow<T> =
        merge(sharedQueue.consume(), broadcastChannels.consume(partition))
    override suspend fun publish(value: T, partition: Int) = sharedQueue.publish(value)
    override suspend fun broadcast(value: T) = broadcastChannels.broadcast(value)

    override suspend fun close() {
        sharedQueue.close()
        broadcastChannels.close()
    }
}
