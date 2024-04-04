package io.airbyte.cdk.core.destination.async.buffer

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong

private val logger = KotlinLogging.logger {}

/**
 * This class is meant to emulate the behavior of a LinkedBlockingQueue, but instead of being
 * bounded on number of items in the queue, it is bounded by the memory it is allowed to use. The
 * amount of memory it is allowed to use can be resized after it is instantiated.
 * <p>
 * This class intentionally hides the underlying queue inside of it. For this class to work, it has
 * to override each method on a queue that adds or removes records from the queue. The Queue
 * interface has a lot of methods to override, and we don't want to spend the time overriding a lot
 * of methods that won't be used. By hiding the queue, we avoid someone accidentally using a queue
 * method that has not been modified. If you need access to another of the queue methods, pattern
 * match adding the memory tracking as seen in {@link HiddenQueue}, and then delegate to that method
 * from this top-level class.
 *
 * @param <E> type in the queue
 */
class MemoryBoundedLinkedBlockingQueue<E>(maxMemoryUsage: Long) {
    private val hiddenQueue: HiddenQueue<E> = HiddenQueue(maxMemoryUsage)

    fun getCurrentMemoryUsage(): Long {
        return hiddenQueue.currentMemoryUsage.get()
    }

    fun addMaxMemory(maxMemoryUsage: Long) {
        hiddenQueue.maxMemoryUsage.addAndGet(maxMemoryUsage)
    }

    fun size(): Int {
        return hiddenQueue.size
    }

    fun offer(
        e: E,
        itemSizeInBytes: Long,
    ): Boolean {
        return hiddenQueue.offer(e, itemSizeInBytes)
    }

    fun peek(): MemoryItem<E>? {
        return hiddenQueue.peek()
    }

    @Throws(InterruptedException::class)
    fun take(): MemoryItem<E> {
        return hiddenQueue.take()
    }

    fun poll(): MemoryItem<E>? {
        return hiddenQueue.poll()
    }

    @Throws(InterruptedException::class)
    fun poll(
        timeout: Long,
        unit: TimeUnit,
    ): MemoryItem<E>? {
        return hiddenQueue.poll(timeout, unit)
    }

    fun getMaxMemoryUsage(): Long {
        return hiddenQueue.getMaxMemoryUsage()
    }

    data class MemoryItem<E>(val item: E, val size: Long)

    class HiddenQueue<E>(maxMemoryUsage: Long) : LinkedBlockingQueue<MemoryItem<E>>() {
        val currentMemoryUsage = AtomicLong(0)
        val maxMemoryUsage = AtomicLong(maxMemoryUsage)

        fun getMaxMemoryUsage(): Long {
            return maxMemoryUsage.get()
        }

        fun offer(
            e: E,
            itemSizeInBytes: Long,
        ): Boolean {
            val newMemoryUsage = currentMemoryUsage.addAndGet(itemSizeInBytes)
            if (newMemoryUsage <= maxMemoryUsage.get()) {
                val success = super.offer(MemoryItem(e, itemSizeInBytes))
                if (!success) {
                    currentMemoryUsage.addAndGet(-itemSizeInBytes)
                }
                logger.debug { "offer status: $success" }
                return success
            } else {
                currentMemoryUsage.addAndGet(-itemSizeInBytes)
                logger.debug { "offer failed" }
                return false
            }
        }

        override fun take(): MemoryItem<E> {
            val memoryItem = super.take()
            currentMemoryUsage.addAndGet(-memoryItem.size)
            return memoryItem
        }

        @Override
        override fun poll(): MemoryItem<E>? {
            val memoryItem = super.poll()
            if (memoryItem != null) {
                currentMemoryUsage.addAndGet(-memoryItem.size)
                return memoryItem
            }
            return null
        }

        @Override
        override fun poll(
            timeout: Long,
            unit: TimeUnit,
        ): MemoryItem<E>? {
            val memoryItem = super.poll(timeout, unit)
            if (memoryItem != null) {
                currentMemoryUsage.addAndGet(-memoryItem.size)
                return memoryItem
            }
            return null
        }
    }
}
