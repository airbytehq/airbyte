/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.util.function.Consumer

/**
 * POJO abstraction representing one discrete buffer read. This allows ergonomics dequeues by
 * [io.airbyte.cdk.integrations.destination.async.FlushWorkers].
 *
 * The contained stream **IS EXPECTED to be a BOUNDED** stream. Returning a boundless stream has
 * undefined behaviour.
 *
 * Once done, consumers **MUST** invoke [.close]. As the [.batch] has already been retrieved from
 * in-memory buffers, we need to update [GlobalMemoryManager] to reflect the freed up memory and
 * avoid memory leaks.
 */
class MemoryAwareMessageBatch(
    val data: List<StreamAwareQueue.MessageWithMeta>,
    val sizeInBytes: Long,
    private val memoryManager: GlobalMemoryManager,
    private val stateManager: GlobalAsyncStateManager,
) : AutoCloseable {
    @Throws(Exception::class)
    override fun close() {
        memoryManager.free(sizeInBytes)
    }

    /**
     * For the batch, marks all the states that have now been flushed. Also writes the states that
     * can be flushed back to platform via stateManager.
     */
    fun flushStates(
        stateIdToCount: Map<Long, Long>,
        outputRecordCollector: Consumer<AirbyteMessage>,
    ) {
        stateIdToCount.forEach { (stateId: Long, count: Long) ->
            stateManager.decrement(
                stateId,
                count,
            )
        }
        stateManager.flushStates(outputRecordCollector)
    }
}
