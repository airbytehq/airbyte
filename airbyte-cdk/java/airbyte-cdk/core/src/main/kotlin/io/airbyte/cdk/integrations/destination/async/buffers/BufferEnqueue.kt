/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.Optional
import java.util.concurrent.ConcurrentMap
import org.apache.mina.util.ConcurrentHashSet

/**
 * Represents the minimal interface over the underlying buffer queues required for enqueue
 * operations with the aim of minimizing lower-level queue access.
 */
class BufferEnqueue(
    private val memoryManager: GlobalMemoryManager,
    private val buffers: ConcurrentMap<StreamDescriptor, StreamAwareQueue>,
    private val stateManager: GlobalAsyncStateManager,
    private val streamsWithSuccessStatus: ConcurrentHashSet<StreamDescriptor>,
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
        defaultNamespace: Optional<String>,
    ) {
        when (message.type) {
            AirbyteMessage.Type.RECORD -> {
                handleRecord(message, sizeInBytes)
            }
            AirbyteMessage.Type.STATE -> {
                stateManager.trackState(message, sizeInBytes.toLong(), defaultNamespace.orElse(""))
            }
            AirbyteMessage.Type.TRACE -> {
                // There are many types of trace messages, but we only care about stream status messages
                // with status=COMPLETE.
                message.trace?.streamStatus?.let {
                    if (it.status == AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE) {
                        streamsWithSuccessStatus.add(it.streamDescriptor)
                    }
                }
            }
            else -> {}
        }
    }

    private fun handleRecord(
        message: PartialAirbyteMessage,
        sizeInBytes: Int,
    ) {
        val streamDescriptor = extractStateFromRecord(message)
        val queue =
            buffers.computeIfAbsent(
                streamDescriptor,
            ) {
                StreamAwareQueue(memoryManager.requestMemory())
            }
        val stateId = stateManager.getStateIdAndIncrementCounter(streamDescriptor)

        var addedToQueue = queue.offer(message, sizeInBytes.toLong(), stateId)

        var i = 0
        while (!addedToQueue) {
            val newlyAllocatedMemory = memoryManager.requestMemory()
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

    companion object {
        private fun extractStateFromRecord(message: PartialAirbyteMessage): StreamDescriptor {
            return StreamDescriptor()
                .withNamespace(message.record?.namespace)
                .withName(message.record?.stream)
        }
    }
}
