package io.airbyte.cdk.core.destination.async.buffer

import io.airbyte.cdk.core.destination.async.GlobalMemoryManager
import io.airbyte.cdk.core.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.util.function.Consumer

/**
 * POJO abstraction representing one discrete buffer read. This allows ergonomics dequeues by
 * {@link io.airbyte.cdk.core.destination.aysnc.FlushWorkers}.
 * <p>
 * The contained stream **IS EXPECTED to be a BOUNDED** stream. Returning a boundless stream has
 * undefined behaviour.
 * <p>
 * Once done, consumers **MUST** invoke {@link #close()}. As the {@link #batch} has already been
 * retrieved from in-memory buffers, we need to update {@link GlobalMemoryManager} to reflect the
 * freed up memory and avoid memory leaks.
 */
class MemoryAwareMessageBatch(
    val batch: List<StreamAwareQueue.MessageWithMeta>,
    val sizeInBytes: Long,
    private val memoryManager: GlobalMemoryManager,
    private val stateManager: GlobalAsyncStateManager,
) : AutoCloseable {
    @Throws(Exception::class)
    override fun close() {
        memoryManager.free(sizeInBytes)
    }

    fun getData(): List<StreamAwareQueue.MessageWithMeta> {
        return batch
    }

    /**
     * For the batch, marks all the states that have now been flushed. Also writes the states that can
     * be flushed back to platform via stateManager.
     *
     *
     */
    fun flushStates(
        stateIdToCount: Map<Long, Long>,
        outputRecordCollector: Consumer<AirbyteMessage>,
    ) {
        stateIdToCount.forEach { (stateId: Long, count: Long) ->
            stateManager.decrement(stateId, count)
        }
        stateManager.flushStates(outputRecordCollector)
    }
}
