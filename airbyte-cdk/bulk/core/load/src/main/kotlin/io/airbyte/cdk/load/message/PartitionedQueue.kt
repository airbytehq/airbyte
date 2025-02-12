/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.CloseableCoroutine
import kotlinx.coroutines.flow.Flow

class PartitionedQueue<T>(private val queues: Array<MessageQueue<T>>) : CloseableCoroutine {
    val partitions = queues.size

    fun consume(partition: Int): Flow<T> {
        if (partition < 0 || partition >= queues.size) {
            throw IllegalArgumentException("Invalid partition: $partition")
        }
        return queues[partition].consume()
    }

    suspend fun publish(value: T, partition: Int) {
        if (partition < 0 || partition >= queues.size) {
            throw IllegalArgumentException("Invalid partition: $partition")
        }
        queues[partition].publish(value)
    }

    suspend fun broadcast(value: T) = queues.forEach { it.publish(value) }

    override suspend fun close() {
        queues.forEach { it.close() }
    }
}
