/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Instant
import java.util.LinkedList
import java.util.Optional
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.locks.ReentrantLock

/**
 * Represents the minimal interface over the underlying buffer queues required for dequeue
 * operations with the aim of minimizing lower-level queue access.
 *
 * Aside from [.take], all public methods in this class represents queue metadata required to
 * determine buffer flushing.
 */
// todo (cgardens) - make all the metadata methods more efficient.
class BufferDequeue(
    private val memoryManager: GlobalMemoryManager,
    private val buffers: ConcurrentMap<StreamDescriptor, StreamAwareQueue>,
    private val stateManager: GlobalAsyncStateManager,
) {
    private val bufferLocks: ConcurrentMap<StreamDescriptor, ReentrantLock> = ConcurrentHashMap()

    /**
     * Primary dequeue method. Reads from queue up to optimalBytesToRead OR until the queue is
     * empty.
     *
     * @param streamDescriptor specific buffer to take from
     * @param optimalBytesToRead bytes to read, if possible
     * @return autocloseable batch object, that frees memory.
     */
    fun take(
        streamDescriptor: StreamDescriptor,
        optimalBytesToRead: Long,
    ): MemoryAwareMessageBatch {
        val lock: ReentrantLock =
            bufferLocks.computeIfAbsent(
                streamDescriptor,
            ) {
                ReentrantLock()
            }
        lock.lock()

        val queue: StreamAwareQueue? = buffers[streamDescriptor]

        try {
            val bytesRead = AtomicLong()

            val output: MutableList<StreamAwareQueue.MessageWithMeta> = LinkedList()
            while (queue!!.size() > 0) {
                val memoryItem:
                    MemoryBoundedLinkedBlockingQueue.MemoryItem<StreamAwareQueue.MessageWithMeta> =
                    queue.peek().orElseThrow()

                // otherwise pull records until we hit the memory limit.
                val newSize: Long = (memoryItem.size) + bytesRead.get()
                if (newSize <= optimalBytesToRead) {
                    memoryItem.size.let { bytesRead.addAndGet(it) }
                    queue.poll()?.item?.let { output.add(it) }
                } else {
                    break
                }
            }

            if (queue.isEmpty) {
                val batchSizeBytes: Long = bytesRead.get()
                val allocatedBytes: Long = queue.maxMemoryUsage

                // Free unused allocation for the queue.
                // When the batch flushes it will flush its allocation.
                memoryManager.free(allocatedBytes - batchSizeBytes)

                // Shrink queue to 0 — any new messages will reallocate.
                queue.addMaxMemory(-allocatedBytes)
            } else {
                queue.addMaxMemory(-bytesRead.get())
            }

            return MemoryAwareMessageBatch(
                output,
                bytesRead.get(),
                memoryManager,
                stateManager,
            )
        } finally {
            lock.unlock()
        }
    }

    val bufferedStreams: Set<StreamDescriptor>
        /**
         * The following methods are provide metadata for buffer flushing calculations. Consumers
         * are expected to call it to retrieve the currently buffered streams as a handle to the
         * remaining methods.
         */
        get() = HashSet(buffers.keys)

    val maxQueueSizeBytes: Long
        get() = memoryManager.maxMemoryBytes

    val totalGlobalQueueSizeBytes: Long
        get() = buffers.values.sumOf { obj: StreamAwareQueue -> obj.currentMemoryUsage }

    fun getQueueSizeInRecords(streamDescriptor: StreamDescriptor): Optional<Long> {
        return getBuffer(streamDescriptor).map { buf: StreamAwareQueue -> buf.size().toLong() }
    }

    fun getQueueSizeBytes(streamDescriptor: StreamDescriptor): Optional<Long> {
        return getBuffer(streamDescriptor).map { obj: StreamAwareQueue -> obj.currentMemoryUsage }
    }

    fun getTimeOfLastRecord(streamDescriptor: StreamDescriptor): Optional<Instant> {
        return getBuffer(streamDescriptor).flatMap { obj: StreamAwareQueue ->
            obj.getTimeOfLastMessage()
        }
    }

    private fun getBuffer(streamDescriptor: StreamDescriptor): Optional<StreamAwareQueue> {
        if (buffers.containsKey(streamDescriptor)) {
            return Optional.of(
                (buffers[streamDescriptor])!!,
            )
        }
        return Optional.empty()
    }
}
