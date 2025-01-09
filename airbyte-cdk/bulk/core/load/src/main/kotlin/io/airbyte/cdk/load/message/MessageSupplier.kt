/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.CloseableCoroutine
import kotlinx.coroutines.channels.Channel

interface MessageReader<T> {
    suspend fun get(): T?
}

interface MessageWriter<T> : CloseableCoroutine {
    suspend fun publish(message: T)
}

interface Message<T> : MessageReader<T>, MessageWriter<T>

abstract class ChannelMessage<T> : Message<T> {
    val channel = Channel<T>(Channel.UNLIMITED)

    override suspend fun publish(message: T) = channel.send(message)
    override suspend fun get(): T? = channel.tryReceive().getOrNull()
    override suspend fun close() {
        channel.close()
    }
}

interface MessageSupplier<K, T> {
    fun get(key: K): ChannelMessage<T>
}
