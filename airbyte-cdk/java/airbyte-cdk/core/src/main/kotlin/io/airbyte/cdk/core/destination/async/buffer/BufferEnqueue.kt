package io.airbyte.cdk.core.destination.async.buffer

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.GlobalMemoryManager
import io.airbyte.cdk.core.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.core.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Represents the minimal interface over the underlying buffer queues required for enqueue
 * operations with the aim of minimizing lower-level queue access.
 */
@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class BufferEnqueue(
    private val globalMemoryManager: GlobalMemoryManager,
    private val globalAsyncStateManager: GlobalAsyncStateManager,
    private val asyncBuffers: AsyncBuffers,
) {
    /**
     * Buffer a record. Contains memory management logic to dynamically adjust queue size based via
     * [GlobalMemoryManager] accounting for incoming records.
     *
     * @param message to buffer
     * @param sizeInBytes
     */
    fun addRecord(
        message: PartialAirbyteMessage,
        sizeInBytes: Int,
        defaultNamespace: String,
    ) {
        if (message.type == AirbyteMessage.Type.RECORD) {
            handleRecord(message, sizeInBytes)
        } else if (message.type == AirbyteMessage.Type.STATE) {
            globalAsyncStateManager.trackState(message, sizeInBytes.toLong(), defaultNamespace)
        }
    }

    private fun handleRecord(
        message: PartialAirbyteMessage,
        sizeInBytes: Int,
    ) {
        val streamDescriptor = extractStateFromRecord(message)
        val queue: StreamAwareQueue =
            asyncBuffers.buffers.computeIfAbsent(
                streamDescriptor,
            ) { StreamAwareQueue(globalMemoryManager.requestMemory()) }
        val stateId: Long = globalAsyncStateManager.getStateIdAndIncrementCounter(streamDescriptor)

        var addedToQueue = queue.offer(message, sizeInBytes.toLong(), stateId)

        var i = 0
        while (!addedToQueue) {
            val newlyAllocatedMemory: Long = globalMemoryManager.requestMemory()
            if (newlyAllocatedMemory > 0) {
                queue.addMaxMemory(newlyAllocatedMemory)
            }
            addedToQueue = queue.offer(message, sizeInBytes.toLong(), stateId)
            i++
            if (i > 5) {
                try {
                    Thread.sleep(500)
                } catch (e: InterruptedException) {
                    throw RuntimeException(e)
                }
            }
        }
    }

    private fun extractStateFromRecord(message: PartialAirbyteMessage): StreamDescriptor {
        return StreamDescriptor()
            .withNamespace(message.record?.namespace)
            .withName(message.record?.stream)
    }
}
