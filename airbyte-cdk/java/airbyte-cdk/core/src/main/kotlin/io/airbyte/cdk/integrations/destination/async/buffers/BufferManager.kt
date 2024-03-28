/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.destination.async.AirbyteFileUtils
import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit
import org.apache.commons.io.FileUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory

private val logger = KotlinLogging.logger {}

class BufferManager
@JvmOverloads
constructor(
    maxMemory: Long = (Runtime.getRuntime().maxMemory() * MEMORY_LIMIT_RATIO).toLong(),
) {
    @get:VisibleForTesting val buffers: ConcurrentMap<StreamDescriptor, StreamAwareQueue>
    val bufferEnqueue: BufferEnqueue
    val bufferDequeue: BufferDequeue

    @get:VisibleForTesting val memoryManager: GlobalMemoryManager

    val stateManager: GlobalAsyncStateManager
    private val debugLoop: ScheduledExecutorService

    /**
     * @param maxMemory the amount of estimated memory we allow for all buffers. The
     * GlobalMemoryManager will apply back pressure once this quota is filled. "Memory" can be
     * released back once flushing finishes. This number should be large enough we don't block
     * reading unnecessarily, but small enough we apply back pressure before OOMing.
     */
    init {
        LOGGER.info(
            "Max 'memory' available for buffer allocation {}",
            FileUtils.byteCountToDisplaySize(maxMemory),
        )
        memoryManager = GlobalMemoryManager(maxMemory)
        this.stateManager = GlobalAsyncStateManager(memoryManager)
        buffers = ConcurrentHashMap()
        bufferEnqueue = BufferEnqueue(memoryManager, buffers, stateManager)
        bufferDequeue = BufferDequeue(memoryManager, buffers, stateManager)
        debugLoop = Executors.newSingleThreadScheduledExecutor()
        debugLoop.scheduleAtFixedRate(
            { this.printQueueInfo() },
            0,
            DEBUG_PERIOD_SECS,
            TimeUnit.SECONDS,
        )
    }

    /**
     * Closing a queue will flush all items from it. For this reason, this method needs to be called
     * after [io.airbyte.cdk.integrations.destination.async.FlushWorkers.close]. This allows the
     * upload workers to make sure all items in the queue has been flushed.
     */
    @Throws(Exception::class)
    fun close() {
        debugLoop.shutdownNow()
        logger.info { "Buffers cleared.." }
    }

    private fun printQueueInfo() {
        val queueInfo = StringBuilder().append("[ASYNC QUEUE INFO] ")
        val messages = ArrayList<String>()

        messages.add(
            String.format(
                "Global: max: %s, allocated: %s (%s MB), %% used: %s",
                AirbyteFileUtils.byteCountToDisplaySize(memoryManager.maxMemoryBytes),
                AirbyteFileUtils.byteCountToDisplaySize(
                    memoryManager.currentMemoryBytes.get(),
                ),
                memoryManager.currentMemoryBytes.toDouble() / 1024 / 1024,
                memoryManager.currentMemoryBytes.toDouble() / memoryManager.maxMemoryBytes,
            ),
        )

        for ((key, queue) in buffers) {
            messages.add(
                String.format(
                    "Queue `%s`, num records: %d, num bytes: %s, allocated bytes: %s",
                    key.name,
                    queue.size(),
                    AirbyteFileUtils.byteCountToDisplaySize(queue.currentMemoryUsage),
                    AirbyteFileUtils.byteCountToDisplaySize(queue.maxMemoryUsage),
                ),
            )
        }

        messages.add(stateManager.memoryUsageMessage)

        queueInfo.append(java.lang.String.join(" | ", messages))

        logger.info { queueInfo.toString() }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(BufferManager::class.java)

        private const val DEBUG_PERIOD_SECS = 60L

        const val MEMORY_LIMIT_RATIO: Double = 0.7
    }
}
