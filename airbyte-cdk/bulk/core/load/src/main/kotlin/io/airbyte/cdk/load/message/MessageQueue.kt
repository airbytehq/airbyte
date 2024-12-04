/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.CloseableCoroutine
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.DelicateCoroutinesApi
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow

interface QueueReader<T> {
    suspend fun consume(): Flow<T>
    suspend fun poll(): T?
}

interface QueueWriter<T> : CloseableCoroutine {
    suspend fun publish(message: T)
    fun isClosedForPublish(): Boolean
}

interface MessageQueue<T> : QueueReader<T>, QueueWriter<T>

abstract class ChannelMessageQueue<T> : MessageQueue<T> {
    open val channel = Channel<T>(Channel.UNLIMITED)

    override suspend fun publish(message: T) = channel.send(message)
    override suspend fun consume(): Flow<T> = channel.receiveAsFlow()
    override suspend fun poll(): T? = channel.tryReceive().getOrNull()
    override suspend fun close() {
        channel.close()
    }
    @OptIn(DelicateCoroutinesApi::class)
    override fun isClosedForPublish(): Boolean = channel.isClosedForSend
}

interface MessageQueueSupplier<K, T> {
    fun get(key: K): MessageQueue<T>
}

class LimitedMessageQueue<T>(limit: Int) : ChannelMessageQueue<T>() {
    private val log = KotlinLogging.logger {}
    private val producerCount = AtomicLong(0)
    override val channel = Channel<T>(limit)
    init {
        require(limit > 0) { "Limit must be greater than 0" }
        log.info { "Creating queue (limit=$limit)" }
    }

    fun take(): LimitedMessageQueue<T> {
        val count = producerCount.incrementAndGet()
        log.info { "Taking queue (count=$count)" }
        return this
    }

    override suspend fun close() {
        val count = producerCount.decrementAndGet()
        log.info { "Releasing queue (count=$count)" }
        if (count == 0L) {
            log.info { "Closing queue" }
            channel.close()
        }
    }
}
