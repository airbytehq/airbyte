/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicLong
import kotlin.math.min
import org.apache.commons.io.FileUtils

private val logger = KotlinLogging.logger {}

/**
 * Responsible for managing buffer memory across multiple queues in a thread-safe way. This does not
 * allocate or free memory in the traditional sense, but rather manages based off memory estimates
 * provided by the callers.
 *
 * The goal is to enable maximum allowed memory bounds for each queue to be dynamically adjusted
 * according to the overall available memory. Memory blocks are managed in chunks of
 * [.BLOCK_SIZE_BYTES], and the total amount of memory managed is configured at creation time.
 *
 * As a destination has no information about incoming per-stream records, having static queue sizes
 * can cause unnecessary backpressure on a per-stream basis. By providing a dynamic, global view of
 * buffer memory management, this class allows each queue to release and request memory dynamically,
 * enabling effective sharing of global memory resources across all the queues, and avoiding
 * accidental stream backpressure.
 *
 * This becomes particularly useful in the following scenarios:
 *
 * * 1. When the incoming records belong to a single stream. Dynamic allocation ensures this one
 * stream can utilise all memory.
 * * 2. When the incoming records are from multiple streams, such as with Change Data Capture (CDC).
 * Here, dynamic allocation let us create as many queues as possible, allowing all streams to be
 * processed in parallel without accidental backpressure from unnecessary eager flushing.
 */
class GlobalMemoryManager(val maxMemoryBytes: Long) {
    val currentMemoryBytes = AtomicLong(0)

    fun getCurrentMemoryBytes(): Long {
        return currentMemoryBytes.get()
    }

    /**
     * Requests a block of memory of [.BLOCK_SIZE_BYTES]. Return 0 if memory cannot be freed.
     *
     * @return the size of the allocated block, in bytes
     */
    @Synchronized
    fun requestMemory(): Long {
        // todo(davin): what happens if the incoming record is larger than 30MB?
        if (currentMemoryBytes.get() >= maxMemoryBytes) {
            return 0L
        }

        val freeMem = maxMemoryBytes - currentMemoryBytes.get()
        // Never allocate more than free memory size.
        val toAllocateBytes = min(freeMem.toDouble(), BLOCK_SIZE_BYTES.toDouble()).toLong()
        currentMemoryBytes.addAndGet(toAllocateBytes)

        logger.debug {
            "Memory Requested: max: ${FileUtils.byteCountToDisplaySize(
                maxMemoryBytes,
            )}, allocated: ${FileUtils.byteCountToDisplaySize(
                currentMemoryBytes.get(),
            )}, allocated in this request: ${FileUtils.byteCountToDisplaySize(toAllocateBytes)}"
        }
        return toAllocateBytes
    }

    /**
     * Releases a block of memory of the given size. If the amount of memory released exceeds the
     * current memory allocation, a warning will be logged.
     *
     * @param bytes the size of the block to free, in bytes
     */
    fun free(bytes: Long) {
        logger.info { "Freeing $bytes bytes.." }
        currentMemoryBytes.addAndGet(-bytes)

        val currentMemory = currentMemoryBytes.get()
        if (currentMemory < 0) {
            logger.info { "Freed more memory than allocated ($bytes of ${currentMemory + bytes })" }
        }
    }

    companion object {
        // In cases where a queue is rapidly expanding, a larger block size allows less allocation
        // calls. On
        // the flip size, a smaller block size allows more granular memory management. Since this
        // overhead
        // is minimal for now, err on a smaller block sizes.
        const val BLOCK_SIZE_BYTES: Long =
            (10 * 1024 * 1024 // 10MB
                )
                .toLong()
    }
}
