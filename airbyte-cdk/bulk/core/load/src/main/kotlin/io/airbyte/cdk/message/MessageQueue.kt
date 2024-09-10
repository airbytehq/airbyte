/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.channels.Channel

interface Sized {
    val sizeBytes: Long
}

interface MessageQueue<K, T : Sized> {
    suspend fun acquireQueueBytesBlocking(bytes: Long)
    suspend fun releaseQueueBytes(bytes: Long)
    suspend fun getChannel(key: K): QueueChannel<T>
}

interface QueueChannel<T : Sized> {
    suspend fun close()
    suspend fun isClosed(): Boolean
    suspend fun send(message: T)
    suspend fun receive(): T
}

/** A channel that blocks when its parent queue has no available memory. */
interface BlockingQueueChannel<T : Sized> : QueueChannel<T> {
    val messageQueue: MessageQueue<*, T>
    val channel: Channel<T>

    override suspend fun send(message: T) {
        if (isClosed()) {
            throw IllegalStateException("Send to closed QueueChannel")
        }
        val estimatedSize = message.sizeBytes
        messageQueue.acquireQueueBytesBlocking(estimatedSize)
        channel.send(message)
    }

    override suspend fun receive(): T {
        if (isClosed()) {
            throw IllegalStateException("Receive from closed QueueChannel")
        }
        val message = channel.receive()
        val estimatedSize = message.sizeBytes
        messageQueue.releaseQueueBytes(estimatedSize)
        return message
    }
}

interface QueueChannelFactory<T : Sized> {
    fun make(messageQueue: MessageQueue<*, T>): QueueChannel<T>
}

/**
 * The default queue channel is just a dumb wrapper around an unlimited kotlin channel of wrapped
 * records.
 *
 * Note: we wrap channel closedness in an atomic boolean because the @[Channel.isClosedForSend] and
 * @[Channel.isClosedForReceive] apis are marked as delicate/experimental.
 */
class DefaultQueueChannel(override val messageQueue: MessageQueue<*, DestinationRecordWrapped>) :
    BlockingQueueChannel<DestinationRecordWrapped> {
    override val channel = Channel<DestinationRecordWrapped>(Channel.UNLIMITED)
    private val closed = AtomicBoolean(false)

    override suspend fun close() {
        if (closed.compareAndSet(false, true)) {
            channel.close()
        }
    }

    override suspend fun isClosed(): Boolean = closed.get()
}

@Singleton
class DefaultQueueChannelFactory : QueueChannelFactory<DestinationRecordWrapped> {
    override fun make(
        messageQueue: MessageQueue<*, DestinationRecordWrapped>
    ): QueueChannel<DestinationRecordWrapped> = DefaultQueueChannel(messageQueue)
}
