/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import java.time.Instant
import java.util.Optional
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

class StreamAwareQueue(maxMemoryUsage: Long) {
    private val timeOfLastMessage: AtomicReference<Instant> = AtomicReference()

    private val memoryAwareQueue: MemoryBoundedLinkedBlockingQueue<MessageWithMeta> =
        MemoryBoundedLinkedBlockingQueue(maxMemoryUsage)

    val currentMemoryUsage: Long
        get() = memoryAwareQueue.currentMemoryUsage

    val maxMemoryUsage: Long
        get() = memoryAwareQueue.maxMemoryUsage

    fun addMaxMemory(maxMemoryUsage: Long) {
        memoryAwareQueue.addMaxMemory(maxMemoryUsage)
    }

    val isEmpty: Boolean
        get() = memoryAwareQueue.size() == 0

    fun getTimeOfLastMessage(): Optional<Instant> {
        // if the queue is empty, the time of last message is irrelevant
        if (size() == 0) {
            return Optional.empty()
        }
        return Optional.ofNullable(timeOfLastMessage.get())
    }

    fun peek(): Optional<MemoryBoundedLinkedBlockingQueue.MemoryItem<MessageWithMeta>> {
        return Optional.ofNullable(memoryAwareQueue.peek())
    }

    fun size(): Int {
        return memoryAwareQueue.size()
    }

    fun offer(
        message: PartialAirbyteMessage,
        messageSizeInBytes: Long,
        stateId: Long,
    ): Boolean {
        if (memoryAwareQueue.offer(MessageWithMeta(message, stateId), messageSizeInBytes)) {
            timeOfLastMessage.set(Instant.now())
            return true
        } else {
            return false
        }
    }

    @Throws(InterruptedException::class)
    fun take(): MemoryBoundedLinkedBlockingQueue.MemoryItem<MessageWithMeta> {
        return memoryAwareQueue.take()
    }

    fun poll(): MemoryBoundedLinkedBlockingQueue.MemoryItem<MessageWithMeta>? {
        return memoryAwareQueue.poll()
    }

    @Throws(InterruptedException::class)
    fun poll(
        timeout: Long,
        unit: TimeUnit,
    ): MemoryBoundedLinkedBlockingQueue.MemoryItem<MessageWithMeta>? {
        return memoryAwareQueue.poll(timeout, unit)
    }

    @JvmRecord data class MessageWithMeta(val message: PartialAirbyteMessage, val stateId: Long)
}
