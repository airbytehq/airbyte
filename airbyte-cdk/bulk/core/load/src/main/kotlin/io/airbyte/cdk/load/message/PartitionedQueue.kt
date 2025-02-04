/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import java.util.concurrent.ConcurrentLinkedQueue
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.consumeAsFlow

class PartitionedQueue<T>(val partitions: Int, capacity: Int = 1) : AutoCloseable {
    private val channel: ConcurrentLinkedQueue<Channel<T>> =
        ConcurrentLinkedQueue((0 until partitions).map { Channel(capacity) })

    suspend fun consume(partition: Int): Flow<T> = channel.elementAt(partition).consumeAsFlow()
    suspend fun publish(value: T, partition: Int) =
        channel.elementAt(partition % partitions).send(value)
    suspend fun broadcast(value: T) = channel.forEach { it.send(value) }

    override fun close() {
        channel.forEach { it.close() }
    }
}
