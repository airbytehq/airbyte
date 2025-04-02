/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.CloseableCoroutine
import io.airbyte.cdk.load.util.setOnce
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow

interface QueueReader<T> {
    fun consume(): Flow<T>
    suspend fun poll(): T?
}

interface QueueWriter<T> : CloseableCoroutine {
    suspend fun publish(message: T)
    fun isClosedForPublish(): Boolean
}

interface MessageQueue<T> : QueueReader<T>, QueueWriter<T>

open class ChannelMessageQueue<T>(val channel: Channel<T>) : MessageQueue<T> {
    private val isClosed = AtomicBoolean(false)

    override suspend fun publish(message: T) = channel.send(message)
    override fun consume(): Flow<T> = channel.receiveAsFlow()
    override suspend fun poll(): T? = channel.tryReceive().getOrNull()
    override suspend fun close() {
        if (isClosed.setOnce()) {
            channel.close()
        }
    }
    override fun isClosedForPublish(): Boolean = isClosed.get()
}

interface MessageQueueSupplier<K, T> {
    fun get(key: K): MessageQueue<T>
}
