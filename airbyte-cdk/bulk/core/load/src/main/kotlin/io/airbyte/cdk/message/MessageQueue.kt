/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow

interface MessageQueue<T> {
    suspend fun publish(message: T)
    suspend fun consume(): Flow<T>
    suspend fun close()
}

abstract class ChannelMessageQueue<T> : MessageQueue<T> {
    val channel = Channel<T>(Channel.UNLIMITED)

    override suspend fun publish(message: T) = channel.send(message)
    override suspend fun consume(): Flow<T> = channel.receiveAsFlow()
    override suspend fun close() {
        channel.close()
    }
}

interface MessageQueueSupplier<K, T> {
    fun get(key: K): MessageQueue<T>
}
