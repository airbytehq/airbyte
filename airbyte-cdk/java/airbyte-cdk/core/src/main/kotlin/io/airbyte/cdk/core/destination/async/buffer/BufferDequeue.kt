package io.airbyte.cdk.core.destination.async.buffer

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.GlobalMemoryManager
import io.airbyte.cdk.core.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
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
 * <p>
 * Aside from {@link #take(StreamDescriptor, long)}, all public methods in this class represents
 * queue metadata required to determine buffer flushing.
 */
// todo (cgardens) - make all the metadata methods more efficient.
@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class BufferDequeue(
    private val globalMemoryManager: GlobalMemoryManager,
    private val globalAsyncStateManager: GlobalAsyncStateManager,
    private val asyncBuffers: AsyncBuffers,
) {
    private val bufferLocks: ConcurrentMap<StreamDescriptor, ReentrantLock> = ConcurrentHashMap()

    /**
     * Primary dequeue method. Reads from queue up to optimalBytesToRead OR until the queue is empty.
     *
     * @param streamDescriptor specific buffer to take from
     * @param optimalBytesToRead bytes to read, if possible
     * @return autocloseable batch object, that frees memory.
     */
    fun take(
        streamDescriptor: StreamDescriptor?,
        optimalBytesToRead: Long,
    ): MemoryAwareMessageBatch {
        val lock: ReentrantLock = bufferLocks.computeIfAbsent(streamDescriptor) { ReentrantLock() }
        lock.lock()

        val queue: StreamAwareQueue? = asyncBuffers.buffers[streamDescriptor]

        try {
            val bytesRead = AtomicLong()

            val output: MutableList<StreamAwareQueue.MessageWithMeta> = LinkedList()
            if (queue != null) {
                while (queue.size() > 0) {
                    val memoryItem = queue.peek().orElseThrow()

                    // otherwise pull records until we hit the memory limit.
                    val newSize = memoryItem.size + bytesRead.get()
                    if (newSize <= optimalBytesToRead) {
                        bytesRead.addAndGet(memoryItem.size)
                        queue.poll()?.item?.let { output.add(it) }
                    } else {
                        break
                    }
                }

                if (queue.isEmpty()) {
                    val batchSizeBytes = bytesRead.get()
                    val allocatedBytes = queue.getMaxMemoryUsage()

                    // Free unused allocation for the queue.
                    // When the batch flushes it will flush its allocation.
                    globalMemoryManager.free(allocatedBytes - batchSizeBytes)

                    // Shrink queue to 0 — any new messages will reallocate.
                    queue.addMaxMemory(-allocatedBytes)
                } else {
                    queue.addMaxMemory(-bytesRead.get())
                }
            }

            return MemoryAwareMessageBatch(
                output,
                bytesRead.get(),
                globalMemoryManager,
                globalAsyncStateManager,
            )
        } finally {
            lock.unlock()
        }
    }

    /**
     * The following methods are provide metadata for buffer flushing calculations. Consumers are
     * expected to call it to retrieve the currently buffered streams as a handle to the remaining
     * methods.
     */
    fun getBufferedStreams(): Set<StreamDescriptor> {
        return HashSet<StreamDescriptor>(asyncBuffers.buffers.keys)
    }

    fun getMaxQueueSizeBytes(): Long {
        return globalMemoryManager.maxMemoryBytes
    }

    fun getTotalGlobalQueueSizeBytes(): Long {
        return asyncBuffers.buffers.values.stream()
            .map { obj: StreamAwareQueue -> obj.getCurrentMemoryUsage() }.mapToLong { obj: Long -> obj }.sum()
    }

    fun getQueueSizeInRecords(streamDescriptor: StreamDescriptor): Optional<Long> {
        return getBuffer(streamDescriptor).map { buf: StreamAwareQueue ->
            buf.size()
                .toLong()
        }
    }

    fun getQueueSizeBytes(streamDescriptor: StreamDescriptor): Optional<Long> {
        return getBuffer(streamDescriptor).map { obj: StreamAwareQueue -> obj.getCurrentMemoryUsage() }
    }

    fun getTimeOfLastRecord(streamDescriptor: StreamDescriptor): Optional<Instant> {
        return getBuffer(streamDescriptor).flatMap { obj: StreamAwareQueue -> obj.getTimeOfLastMessage() }
    }

    private fun getBuffer(streamDescriptor: StreamDescriptor): Optional<StreamAwareQueue> {
        if (asyncBuffers.buffers.containsKey(streamDescriptor)) {
            return Optional.ofNullable<StreamAwareQueue>(asyncBuffers.buffers[streamDescriptor])
        }
        return Optional.empty()
    }
}
