/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.CloseableCoroutine
import kotlinx.coroutines.flow.Flow

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
