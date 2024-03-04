package io.airbyte.cdk.core.destination.async

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.buffer.BufferMemory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import org.apache.commons.io.FileUtils
import java.util.concurrent.atomic.AtomicLong
import kotlin.math.min

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class GlobalMemoryManager(bufferMemory: BufferMemory) {
    val currentMemoryBytes: AtomicLong = AtomicLong(0)
    val maxMemoryBytes = bufferMemory.getMemoryLimit()

    companion object {
        // In cases where a queue is rapidly expanding, a larger block size allows less allocation calls. On
        // the flip size, a smaller block size allows more granular memory management. Since this overhead
        // is minimal for now, err on a smaller block sizes.
        const val BLOCK_SIZE_BYTES: Long = (10 * 1024 * 1024).toLong() // 10MB
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
        val toAllocateBytes =
            min(freeMem.toDouble(), BLOCK_SIZE_BYTES.toDouble())
                .toLong()
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
            logger.info { "Freed more memory than allocated ($bytes of ${currentMemory + bytes})" }
        }
    }
}
