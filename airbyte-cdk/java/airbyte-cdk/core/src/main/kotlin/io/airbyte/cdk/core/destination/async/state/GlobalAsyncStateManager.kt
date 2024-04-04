package io.airbyte.cdk.core.destination.async.state

import com.google.common.base.Preconditions
import com.google.common.base.Strings
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.GlobalMemoryManager
import io.airbyte.cdk.core.destination.async.model.PartialAirbyteMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import org.apache.commons.io.FileUtils
import org.apache.commons.lang3.tuple.ImmutablePair
import java.time.Instant
import java.util.Optional
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.LinkedBlockingDeque
import java.util.concurrent.atomic.AtomicLong
import java.util.function.Consumer

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class GlobalAsyncStateManager(
    private val globalMemoryManager: GlobalMemoryManager,
) {
    private val aliasIds = mutableSetOf<Long>()
    private var arrivalNumber = 0L
    private var descToStateIdQ = ConcurrentHashMap<StreamDescriptor, LinkedBlockingDeque<Long>>()
    private val lock = Object()
    private val memoryAllocated = AtomicLong(globalMemoryManager.requestMemory())
    private val memoryUsed = AtomicLong()
    private var preState = true
    private var retroactiveGlobalStateId = 0L
    private val stateIdToCounter = ConcurrentHashMap<Long, AtomicLong>()
    private val stateIdToCounterForPopulatingDestinationStats = ConcurrentHashMap<Long, AtomicLong>()
    private val stateIdToState = ConcurrentHashMap<Long, ImmutablePair<StateMessageWithArrivalNumber, Long>>()
    private var stateType: AirbyteStateType? = AirbyteStateType.STREAM

    companion object {
        val SENTINEL_GLOBAL_DESC: StreamDescriptor = StreamDescriptor().withName(UUID.randomUUID().toString())
    }

    /**
     * Simplify internal tracking by providing a global always increasing counter for state ids.
     */
    private object StateIdProvider {
        private val pk = AtomicLong(0)

        val nextId: Long
            get() = pk.incrementAndGet()
    }

    private data class StateMessageWithArrivalNumber(val partialAirbyteStateMessage: PartialAirbyteMessage, val arrivalNumber: Long)

    /**
     * Main method to process state messages.
     *
     *
     * The first incoming state message tells us the type of state we are dealing with. We then convert
     * internal data structures if needed.
     *
     *
     * Because state messages are a watermark, all preceding records need to be flushed before the state
     * message can be processed.
     */
    fun trackState(
        message: PartialAirbyteMessage,
        sizeInBytes: Long,
        defaultNamespace: String,
    ) {
        if (preState) {
            convertToGlobalIfNeeded(message)
            preState = false
        }
        // stateType should not change after a conversion.
        Preconditions.checkArgument(stateType == extractStateType(message))

        closeState(message, sizeInBytes, defaultNamespace)
    }

    /**
     * Identical to [.getStateId] except this increments the associated counter
     * by 1. Intended to be called whenever a record is ingested.
     *
     * @param streamDescriptor - stream to get stateId for.
     * @return state id
     */
    fun getStateIdAndIncrementCounter(streamDescriptor: StreamDescriptor): Long {
        return getStateIdAndIncrement(streamDescriptor, 1)
    }

    /**
     * Each decrement represent one written record for a state. A zero counter means there are no more
     * inflight records associated with a state and the state can be flushed.
     *
     * @param stateId reference to a state.
     * @param count to decrement.
     */
    fun decrement(
        stateId: Long,
        count: Long,
    ) {
        synchronized(lock) {
            logger.trace { "decrementing state id: $stateId, count: $count" }
            stateIdToCounter[getStateAfterAlias(stateId)]?.addAndGet(-count)
        }
    }

    /**
     * Flushes state messages with no more inflight records i.e. counter = 0 across all streams.
     * Intended to be called by [io.airbyte.cdk.core.destination.async.FlushWorkers] after
     * a worker has finished flushing its record batch.
     *
     *
     */
    fun flushStates(outputRecordCollector: Consumer<AirbyteMessage>) {
        var bytesFlushed = 0L
        synchronized(lock) {
            for ((_, stateIdQueue) in descToStateIdQ) {
                // Remove all states with 0 counters.
                // Per-stream synchronized is required to make sure the state (at the head of the queue)
                // logic is applied to is the state actually removed.

                while (true) {
                    val oldestStateId = stateIdQueue.peek() ?: break
                    // no state to flush for this stream

                    // technically possible this map hasn't been updated yet.
                    // This can be if you call the flush method if there are 0 records/states
                    val oldestStateCounter = stateIdToCounter[oldestStateId] ?: break

                    val oldestState =
                        stateIdToState[oldestStateId] ?: break
                    // no state to flush for this stream

                    val allRecordsCommitted = oldestStateCounter.get() == 0L
                    if (allRecordsCommitted) {
                        val stateMessage =
                            oldestState.getLeft()
                        val flushedRecordsAssociatedWithState =
                            stateIdToCounterForPopulatingDestinationStats[oldestStateId]!!
                                .toDouble()

                        logger.info {
                            "State with arrival number ${stateMessage.arrivalNumber} emitted from thread ${Thread.currentThread().name} at ${Instant.now()}"
                        }
                        val message =
                            Jsons.deserialize(
                                stateMessage.partialAirbyteStateMessage.serialized,
                                AirbyteMessage::class.java,
                            )
                        message.state.destinationStats =
                            AirbyteStateStats()
                                .withRecordCount(flushedRecordsAssociatedWithState)
                        outputRecordCollector.accept(message)

                        bytesFlushed += oldestState.getRight()

                        // cleanup
                        stateIdQueue.poll()
                        stateIdToState.remove(oldestStateId)
                        stateIdToCounter.remove(oldestStateId)
                        stateIdToCounterForPopulatingDestinationStats.remove(oldestStateId)
                    } else {
                        break
                    }
                }
            }
        }

        freeBytes(bytesFlushed)
    }

    fun getMemoryUsageMessage(): String {
        return "State Manager memory usage: Allocated: ${FileUtils.byteCountToDisplaySize(
            memoryAllocated.get(),
        )}, Used: ${FileUtils.byteCountToDisplaySize(
            memoryUsed.get(),
        )}, percentage Used ${memoryUsed.get().toDouble() / memoryAllocated.get()}"
    }

    /**
     * Given the size of a state message, tracks how much memory the manager is using and requests
     * additional memory from the memory manager if needed.
     *
     * @param sizeInBytes size of the state message
     */
    private fun allocateMemoryToState(sizeInBytes: Long) {
        if (memoryAllocated.get() < memoryUsed.get() + sizeInBytes) {
            while (memoryAllocated.get() < memoryUsed.get() + sizeInBytes) {
                memoryAllocated.addAndGet(globalMemoryManager.requestMemory())
                try {
                    logger.debug {
                        "Insufficient memory to store state message. Allocated: ${FileUtils.byteCountToDisplaySize(
                            memoryAllocated.get(),
                        )}, Used: ${FileUtils.byteCountToDisplaySize(
                            memoryUsed.get(),
                        )}, Size of State Msg: ${FileUtils.byteCountToDisplaySize(
                            sizeInBytes,
                        )}, Needed: ${FileUtils.byteCountToDisplaySize(sizeInBytes - (memoryAllocated.get() - memoryUsed.get()))}"
                    }
                    Thread.sleep(1000)
                } catch (e: InterruptedException) {
                    throw RuntimeException(e)
                }
            }
            logger.debug { getMemoryUsageMessage() }
        }
    }

    /**
     * When a state message is received, 'close' the previous state to associate the existing state id
     * to the newly arrived state message. We also increment the state id in preparation for the next
     * state message.
     */
    private fun closeState(
        message: PartialAirbyteMessage,
        sizeInBytes: Long,
        defaultNamespace: String,
    ) {
        val resolvedDescriptor =
            extractStream(message, defaultNamespace).orElse(
                SENTINEL_GLOBAL_DESC,
            )
        synchronized(lock) {
            logger.info { "State with arrival number $arrivalNumber received" }
            stateIdToState[getStateId(resolvedDescriptor)] =
                ImmutablePair.of(
                    StateMessageWithArrivalNumber(
                        message,
                        arrivalNumber,
                    ),
                    sizeInBytes,
                )
            arrivalNumber++
        }
        registerNewStateId(resolvedDescriptor)
        allocateMemoryToState(sizeInBytes)
    }

    private fun convertToGlobalIfNeeded(message: PartialAirbyteMessage) {
        // instead of checking for global or legacy, check for the inverse of stream.
        stateType = extractStateType(message)
        if (stateType != null && stateType != AirbyteStateType.STREAM) { // alias old stream-level state ids to single global state id
            // upon conversion, all previous tracking data structures need to be cleared as we move
            // into the non-STREAM world for correctness.
            synchronized(lock) {
                aliasIds.addAll(
                    descToStateIdQ.values.stream()
                        .flatMap { obj: LinkedBlockingDeque<Long> -> obj.stream() }
                        .toList(),
                )
                descToStateIdQ.clear()
                retroactiveGlobalStateId = StateIdProvider.nextId

                descToStateIdQ[SENTINEL_GLOBAL_DESC] = LinkedBlockingDeque<Long>()
                descToStateIdQ[SENTINEL_GLOBAL_DESC]?.add(retroactiveGlobalStateId)

                val combinedCounter: Long =
                    stateIdToCounter.values
                        .stream()
                        .mapToLong { obj: AtomicLong -> obj.get() }
                        .sum()
                stateIdToCounter.clear()
                stateIdToCounter[retroactiveGlobalStateId] = AtomicLong(combinedCounter)

                val statsCounter: Long =
                    stateIdToCounterForPopulatingDestinationStats.values
                        .stream()
                        .mapToLong { obj: AtomicLong -> obj.get() }
                        .sum()
                stateIdToCounterForPopulatingDestinationStats.clear()
                stateIdToCounterForPopulatingDestinationStats.put(
                    retroactiveGlobalStateId,
                    AtomicLong(statsCounter),
                )
            }
        }
    }

    /**
     * If the user has selected the Destination Namespace as the Destination default while setting up
     * the connector, the platform sets the namespace as null in the StreamDescriptor in the
     * AirbyteMessages (both record and state messages). The destination checks that if the namespace is
     * empty or null, if yes then re-populates it with the defaultNamespace. See
     * {@link io.airbyte.cdk.core.destination.async.AsyncStreamConsumer#accept(String,Integer)}
     * But destination only does this for the record messages. So when state messages arrive without a
     * namespace and since the destination doesn't repopulate it with the default namespace, there is a
     * mismatch between the StreamDescriptor from record messages and state messages. That breaks the
     * logic of the state management class as {@link descToStateIdQ} needs to have consistent
     * StreamDescriptor. This is why while trying to extract the StreamDescriptor from state messages,
     * we check if the namespace is null, if yes then replace it with defaultNamespace to keep it
     * consistent with the record messages.
     */
    private fun extractStream(
        message: PartialAirbyteMessage,
        defaultNamespace: String,
    ): Optional<StreamDescriptor> {
        if (message.state?.type != null && message.state?.type == AirbyteStateMessage.AirbyteStateType.STREAM) {
            val streamDescriptor = message.state?.stream?.streamDescriptor
            if (Strings.isNullOrEmpty(streamDescriptor?.namespace)) {
                return Optional.of(StreamDescriptor().withName(streamDescriptor?.name).withNamespace(defaultNamespace))
            }
            return Optional.ofNullable(streamDescriptor)
        }
        return Optional.empty()
    }

    /**
     * Pass this the number of bytes that were flushed. It will track those internally and if the
     * memoryUsed gets significantly lower than what is allocated, then it will return it to the memory
     * manager. We don't always return to the memory manager to avoid needlessly allocating /
     * de-allocating memory rapidly over a few bytes.
     *
     * @param bytesFlushed bytes that were flushed (and should be removed from memory used).
     */
    private fun freeBytes(bytesFlushed: Long) {
        logger.debug {
            "Bytes flushed memory to store state message. Allocated: ${FileUtils.byteCountToDisplaySize(
                memoryAllocated.get(),
            )}, Used: ${FileUtils.byteCountToDisplaySize(
                memoryUsed.get(),
            )}, Flushed: ${FileUtils.byteCountToDisplaySize(bytesFlushed)}, % Used: ${memoryUsed.get().toDouble() / memoryAllocated.get()}"
        }
        globalMemoryManager.free(bytesFlushed)
        memoryAllocated.addAndGet(-bytesFlushed)
        memoryUsed.addAndGet(-bytesFlushed)
        logger.debug { "Returned ${FileUtils.byteCountToDisplaySize(bytesFlushed)} of memory back to the memory manager." }
    }

    private fun extractStateType(message: PartialAirbyteMessage): AirbyteStateMessage.AirbyteStateType? {
        return if (message.state?.type == null) {
            // Treated the same as GLOBAL.
            AirbyteStateMessage.AirbyteStateType.LEGACY
        } else {
            message.state?.type
        }
    }

    private fun getStateAfterAlias(stateId: Long): Long {
        return if (aliasIds.contains(stateId)) {
            retroactiveGlobalStateId
        } else {
            stateId
        }
    }

    /**
     * Return the internal id of a state message. This is the id that should be used to reference a
     * state when interacting with all methods in this class.
     *
     * @param streamDescriptor - stream to get stateId for.
     * @return state id
     */
    private fun getStateId(streamDescriptor: StreamDescriptor): Long {
        return getStateIdAndIncrement(streamDescriptor, 0)
    }

    private fun getStateIdAndIncrement(
        streamDescriptor: StreamDescriptor,
        increment: Long,
    ): Long {
        val resolvedDescriptor =
            if (stateType == AirbyteStateMessage.AirbyteStateType.STREAM) streamDescriptor else SENTINEL_GLOBAL_DESC
        // As concurrent collections do not guarantee data consistency when iterating, use `get` instead of
        // `containsKey`.
        if (descToStateIdQ[resolvedDescriptor] == null) {
            registerNewStreamDescriptor(resolvedDescriptor)
        }
        synchronized(lock) {
            val stateId = descToStateIdQ[resolvedDescriptor]!!.peekLast()
            val update = stateIdToCounter[stateId]!!.addAndGet(increment)
            if (increment >= 0) {
                stateIdToCounterForPopulatingDestinationStats[stateId]!!.addAndGet(increment)
            }
            logger.trace { "State id: $stateId, count: $update" }
            return stateId
        }
    }

    private fun registerNewStateId(resolvedDescriptor: StreamDescriptor) {
        val stateId = StateIdProvider.nextId
        synchronized(lock) {
            stateIdToCounter[stateId] = AtomicLong(0)
            stateIdToCounterForPopulatingDestinationStats[stateId] = AtomicLong(0)
            descToStateIdQ[resolvedDescriptor]!!.add(stateId)
        }
    }

    private fun registerNewStreamDescriptor(resolvedDescriptor: StreamDescriptor) {
        synchronized(lock) {
            descToStateIdQ.put(resolvedDescriptor, LinkedBlockingDeque<Long>())
        }
        registerNewStateId(resolvedDescriptor)
    }
}
