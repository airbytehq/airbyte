/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.CloseableCoroutine
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow

interface QueueReader<T> {
    suspend fun consume(): Flow<T>
    suspend fun poll(): T?
}

interface QueueWriter<T> : CloseableCoroutine {
    suspend fun publish(message: T)
}

interface MessageQueue<T> : QueueReader<T>, QueueWriter<T>

abstract class ChannelMessageQueue<T> : MessageQueue<T> {
    val channel = Channel<T>(Channel.UNLIMITED)

    override suspend fun publish(message: T) = channel.send(message)
    override suspend fun consume(): Flow<T> = channel.receiveAsFlow()
    override suspend fun poll(): T? = channel.tryReceive().getOrNull()
    override suspend fun close() {
        channel.close()
    }
}

interface MessageQueueSupplier<K, T> {
    fun get(key: K): MessageQueue<T>
}
