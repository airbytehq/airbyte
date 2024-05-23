/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.state

import com.google.common.base.Preconditions
import com.google.common.base.Strings
import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.Optional
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.LinkedBlockingDeque
import java.util.concurrent.atomic.AtomicLong
import java.util.function.Consumer
import org.apache.commons.io.FileUtils
import org.apache.mina.util.ConcurrentHashSet

private val logger = KotlinLogging.logger {}

/**
 * Responsible for managing state within the Destination. The general approach is a ref counter
 * approach - each state message is associated with a record count. This count represents the number
 * of preceding records. For a state to be emitted, all preceding records have to be written to the
 * destination i.e. the counter is 0.
 *
 * A per-stream state queue is maintained internally, with each state within the queue having a
 * counter. This means we *ALLOW* records succeeding an unemitted state to be written. This
 * decouples record writing from state management at the cost of potentially repeating work if an
 * upstream state is never written.
 *
 * One important detail here is the difference between how PER-STREAM & NON-PER-STREAM is handled.
 * The PER-STREAM case is simple, and is as described above. The NON-PER-STREAM case is slightly
 * tricky. Because we don't know the stream type to begin with, we always assume PER_STREAM until
 * the first state message arrives. If this state message is a GLOBAL state, we alias all existing
 * state ids to a single global state id via a set of alias ids. From then onwards, we use one id -
 * [.SENTINEL_GLOBAL_DESC] regardless of stream. Read [.convertToGlobalIfNeeded] for more detail.
 */
class GlobalAsyncStateManager(private val memoryManager: GlobalMemoryManager) {
    /** Memory that the manager has allocated to it to use. It can ask for more memory as needed. */
    private val memoryAllocated: AtomicLong = AtomicLong(memoryManager.requestMemory())

    /** Memory that the manager is currently using. */
    private val memoryUsed: AtomicLong = AtomicLong()

    private var preState: Boolean = true
    private val descToStateIdQ: ConcurrentMap<StreamDescriptor, LinkedBlockingDeque<Long>> =
        ConcurrentHashMap()

    /**
     * Both [stateIdToCounter] and [stateIdToCounterForPopulatingDestinationStats] are used to
     * maintain a counter for the number of records associated with a give state i.e. before a state
     * was received, how many records were seen until that point. As records are received the value
     * for both are incremented. The difference is the purpose of the two attributes.
     * [stateIdToCounter] is used to determine whether a state is safe to emit or not. This is done
     * by decrementing the value as records are committed to the destination. If the value hits 0,
     * it means all the records associated with a given state have been committed to the
     * destination, it is safe to emit the state back to platform. But because of this we can't use
     * it to determine the actual number of records that are associated with a state to update the
     * value of [AirbyteStateMessage.destinationStats] at the time of emitting the state message.
     * That's where we need [stateIdToCounterForPopulatingDestinationStats], which is only reset
     * when a state message has been emitted.
     */
    private val stateIdToCounter: ConcurrentMap<Long, AtomicLong> = ConcurrentHashMap()
    private val stateIdToCounterForPopulatingDestinationStats: ConcurrentMap<Long, AtomicLong> =
        ConcurrentHashMap()
    private val stateIdToState: ConcurrentMap<Long, Pair<StateMessageWithArrivalNumber, Long>> =
        ConcurrentHashMap()

    // Alias-ing only exists in the non-STREAM case where we have to convert existing state ids to
    // one
    // single global id.
    // This only happens once.
    private val aliasIds: MutableSet<Long> = ConcurrentHashSet()
    private var retroactiveGlobalStateId: Long = 0

    // All access to this field MUST be guarded by a synchronized(lock) block
    private var arrivalNumber: Long = 0

    private val lock: Any = Any()

    // Always assume STREAM to begin, and convert only if needed. Most state is per stream anyway.
    private var stateType: AirbyteStateMessage.AirbyteStateType =
        AirbyteStateMessage.AirbyteStateType.STREAM

    /**
     * Main method to process state messages.
     *
     * The first incoming state message tells us the type of state we are dealing with. We then
     * convert internal data structures if needed.
     *
     * Because state messages are a watermark, all preceding records need to be flushed before the
     * state message can be processed.
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
     * Identical to [.getStateId] except this increments the associated counter by 1. Intended to be
     * called whenever a record is ingested.
     *
     * @param streamDescriptor
     * - stream to get stateId for.
     * @return state id
     */
    fun getStateIdAndIncrementCounter(streamDescriptor: StreamDescriptor): Long {
        return getStateIdAndIncrement(streamDescriptor, 1)
    }

    /**
     * Each decrement represent one written record for a state. A zero counter means there are no
     * more inflight records associated with a state and the state can be flushed.
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
            stateIdToCounter[getStateAfterAlias(stateId)]!!.addAndGet(-count)
        }
    }

    /**
     * Flushes state messages with no more inflight records i.e. counter = 0 across all streams.
     * Intended to be called by [io.airbyte.cdk.integrations.destination.async.FlushWorkers] after a
     * worker has finished flushing its record batch.
     */
    fun flushStates(outputRecordCollector: Consumer<AirbyteMessage>) {
        var bytesFlushed: Long = 0L
        logger.info { "Flushing states" }
        synchronized(lock) {
            for (entry: Map.Entry<StreamDescriptor, LinkedBlockingDeque<Long>?> in
                descToStateIdQ.entries) {
                // Remove all states with 0 counters.
                // Per-stream synchronized is required to make sure the state (at the head of the
                // queue)
                // logic is applied to is the state actually removed.

                val stateIdQueue: LinkedBlockingDeque<Long>? = entry.value
                while (true) {
                    val oldestStateId: Long = stateIdQueue!!.peek() ?: break
                    // no state to flush for this stream

                    // technically possible this map hasn't been updated yet.
                    // This can be if you call the flush method if there are 0 records/states
                    val oldestStateCounter: AtomicLong = stateIdToCounter[oldestStateId] ?: break

                    val oldestState: Pair<StateMessageWithArrivalNumber, Long> =
                        stateIdToState[oldestStateId] ?: break
                    // no state to flush for this stream

                    val allRecordsCommitted: Boolean = oldestStateCounter.get() == 0L
                    if (allRecordsCommitted) {
                        val stateMessage: StateMessageWithArrivalNumber = oldestState.first
                        val flushedRecordsAssociatedWithState: Double =
                            stateIdToCounterForPopulatingDestinationStats[oldestStateId]!!
                                .toDouble()

                        logger.debug {
                            "State with arrival number ${stateMessage.arrivalNumber} emitted from thread ${Thread.currentThread().name} at ${Instant.now()}"
                        }
                        val message: AirbyteMessage =
                            Jsons.deserialize(
                                stateMessage.partialAirbyteStateMessage.serialized,
                                AirbyteMessage::class.java,
                            )
                        message.state.destinationStats =
                            AirbyteStateStats().withRecordCount(flushedRecordsAssociatedWithState)
                        outputRecordCollector.accept(message)

                        bytesFlushed += oldestState.second

                        // cleanup
                        entry.value!!.poll()
                        stateIdToState.remove(oldestStateId)
                        stateIdToCounter.remove(oldestStateId)
                        stateIdToCounterForPopulatingDestinationStats.remove(oldestStateId)
                    } else {
                        break
                    }
                }
            }
        }
        logger.info { "Flushing states complete" }
        freeBytes(bytesFlushed)
    }

    private fun getStateIdAndIncrement(
        streamDescriptor: StreamDescriptor,
        increment: Long,
    ): Long {
        val resolvedDescriptor: StreamDescriptor =
            if (stateType == AirbyteStateMessage.AirbyteStateType.STREAM) streamDescriptor
            else SENTINEL_GLOBAL_DESC
        // As concurrent collections do not guarantee data consistency when iterating, use `get`
        // instead of
        // `containsKey`.
        if (descToStateIdQ[resolvedDescriptor] == null) {
            registerNewStreamDescriptor(resolvedDescriptor)
        }
        synchronized(lock) {
            val stateId: Long = descToStateIdQ[resolvedDescriptor]!!.peekLast()
            val update: Long = stateIdToCounter[stateId]!!.addAndGet(increment)
            if (increment >= 0) {
                stateIdToCounterForPopulatingDestinationStats[stateId]!!.addAndGet(increment)
            }
            logger.trace { "State id: $stateId, count: $update" }
            return stateId
        }
    }

    /**
     * Return the internal id of a state message. This is the id that should be used to reference a
     * state when interacting with all methods in this class.
     *
     * @param streamDescriptor
     * - stream to get stateId for.
     * @return state id
     */
    private fun getStateId(streamDescriptor: StreamDescriptor): Long {
        return getStateIdAndIncrement(streamDescriptor, 0)
    }

    /**
     * Pass this the number of bytes that were flushed. It will track those internally and if the
     * memoryUsed gets signficantly lower than what is allocated, then it will return it to the
     * memory manager. We don't always return to the memory manager to avoid needlessly allocating /
     * de-allocating memory rapidly over a few bytes.
     *
     * @param bytesFlushed bytes that were flushed (and should be removed from memory used).
     */
    private fun freeBytes(bytesFlushed: Long) {
        logger.debug {
            "Bytes flushed memory to store state message. Allocated: " +
                "${FileUtils.byteCountToDisplaySize(memoryAllocated.get())}, " +
                "Used: ${FileUtils.byteCountToDisplaySize(memoryUsed.get())}, " +
                "Flushed: ${FileUtils.byteCountToDisplaySize(bytesFlushed)}, " +
                "% Used: ${memoryUsed.get().toDouble() / memoryAllocated.get()}"
        }

        memoryManager.free(bytesFlushed)
        memoryAllocated.addAndGet(-bytesFlushed)
        memoryUsed.addAndGet(-bytesFlushed)
        logger.debug {
            "Returned ${FileUtils.byteCountToDisplaySize(bytesFlushed)} of memory back to the memory manager."
        }
    }

    private fun convertToGlobalIfNeeded(message: PartialAirbyteMessage) {
        // instead of checking for global or legacy, check for the inverse of stream.
        stateType = extractStateType(message)
        if (
            stateType != AirbyteStateMessage.AirbyteStateType.STREAM
        ) { // alias old stream-level state ids to single global state id
            // upon conversion, all previous tracking data structures need to be cleared as we move
            // into the non-STREAM world for correctness.
            synchronized(lock) {
                aliasIds.addAll(
                    descToStateIdQ.values.flatMap { obj: LinkedBlockingDeque<Long> -> obj },
                )
                descToStateIdQ.clear()
                retroactiveGlobalStateId = StateIdProvider.nextId

                descToStateIdQ[SENTINEL_GLOBAL_DESC] = LinkedBlockingDeque()
                descToStateIdQ[SENTINEL_GLOBAL_DESC]!!.add(retroactiveGlobalStateId)

                val combinedCounter: Long = stateIdToCounter.values.sumOf { it.get() }
                stateIdToCounter.clear()
                stateIdToCounter[retroactiveGlobalStateId] = AtomicLong(combinedCounter)

                val statsCounter: Long =
                    stateIdToCounterForPopulatingDestinationStats.values.sumOf { it.get() }
                stateIdToCounterForPopulatingDestinationStats.clear()
                stateIdToCounterForPopulatingDestinationStats.put(
                    retroactiveGlobalStateId,
                    AtomicLong(statsCounter),
                )
            }
        }
    }

    private fun extractStateType(
        message: PartialAirbyteMessage,
    ): AirbyteStateMessage.AirbyteStateType {
        return if (message.state?.type == null) {
            // Treated the same as GLOBAL.
            AirbyteStateMessage.AirbyteStateType.LEGACY
        } else {
            message.state?.type!!
        }
    }

    /**
     * When a state message is received, 'close' the previous state to associate the existing state
     * id to the newly arrived state message. We also increment the state id in preparation for the
     * next state message.
     */
    private fun closeState(
        message: PartialAirbyteMessage,
        sizeInBytes: Long,
        defaultNamespace: String,
    ) {
        val resolvedDescriptor: StreamDescriptor =
            extractStream(message, defaultNamespace)
                .orElse(
                    SENTINEL_GLOBAL_DESC,
                )
        synchronized(lock) {
            logger.debug { "State with arrival number $arrivalNumber received" }
            stateIdToState[getStateId(resolvedDescriptor)] =
                Pair(
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

    /**
     * Given the size of a state message, tracks how much memory the manager is using and requests
     * additional memory from the memory manager if needed.
     *
     * @param sizeInBytes size of the state message
     */
    private fun allocateMemoryToState(sizeInBytes: Long) {
        if (memoryAllocated.get() < memoryUsed.get() + sizeInBytes) {
            while (memoryAllocated.get() < memoryUsed.get() + sizeInBytes) {
                memoryAllocated.addAndGet(memoryManager.requestMemory())
                try {
                    logger.debug {
                        "Insufficient memory to store state message. " +
                            "Allocated: ${FileUtils.byteCountToDisplaySize(memoryAllocated.get())}, " +
                            "Used: ${FileUtils.byteCountToDisplaySize(memoryUsed.get())}, " +
                            "Size of State Msg: ${FileUtils.byteCountToDisplaySize(sizeInBytes)}, " +
                            "Needed: ${FileUtils.byteCountToDisplaySize(
                                sizeInBytes - (memoryAllocated.get() - memoryUsed.get()),
                            )}"
                    }
                    Thread.sleep(1000)
                } catch (e: InterruptedException) {
                    throw RuntimeException(e)
                }
            }
            logger.debug { memoryUsageMessage }
        }
    }

    val memoryUsageMessage: String
        get() =
            "State Manager memory usage: Allocated: ${FileUtils.byteCountToDisplaySize(memoryAllocated.get())}, Used: ${FileUtils.byteCountToDisplaySize(memoryUsed.get())}, percentage Used ${memoryUsed.get().toDouble() / memoryAllocated.get()}"

    private fun getStateAfterAlias(stateId: Long): Long {
        return if (aliasIds.contains(stateId)) {
            retroactiveGlobalStateId
        } else {
            stateId
        }
    }

    private fun registerNewStreamDescriptor(resolvedDescriptor: StreamDescriptor) {
        synchronized(lock) { descToStateIdQ.put(resolvedDescriptor, LinkedBlockingDeque()) }
        registerNewStateId(resolvedDescriptor)
    }

    private fun registerNewStateId(resolvedDescriptor: StreamDescriptor) {
        val stateId: Long = StateIdProvider.nextId
        synchronized(lock) {
            stateIdToCounter[stateId] = AtomicLong(0)
            stateIdToCounterForPopulatingDestinationStats[stateId] = AtomicLong(0)
            descToStateIdQ[resolvedDescriptor]!!.add(stateId)
        }
    }

    /** Simplify internal tracking by providing a global always increasing counter for state ids. */
    private object StateIdProvider {
        private val pk: AtomicLong = AtomicLong(0)

        val nextId: Long
            get() {
                return pk.incrementAndGet()
            }
    }

    @JvmRecord
    private data class StateMessageWithArrivalNumber(
        val partialAirbyteStateMessage: PartialAirbyteMessage,
        val arrivalNumber: Long,
    )

    companion object {
        private val SENTINEL_GLOBAL_DESC: StreamDescriptor =
            StreamDescriptor()
                .withName(
                    UUID.randomUUID().toString(),
                )

        /**
         * If the user has selected the Destination Namespace as the Destination default while
         * setting up the connector, the platform sets the namespace as null in the StreamDescriptor
         * in the AirbyteMessages (both record and state messages). The destination checks that if
         * the namespace is empty or null, if yes then re-populates it with the defaultNamespace.
         * See [io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer.accept] But
         * destination only does this for the record messages. So when state messages arrive without
         * a namespace and since the destination doesn't repopulate it with the default namespace,
         * there is a mismatch between the StreamDescriptor from record messages and state messages.
         * That breaks the logic of the state management class as [descToStateIdQ] needs to have
         * consistent StreamDescriptor. This is why while trying to extract the StreamDescriptor
         * from state messages, we check if the namespace is null, if yes then replace it with
         * defaultNamespace to keep it consistent with the record messages.
         */
        private fun extractStream(
            message: PartialAirbyteMessage,
            defaultNamespace: String,
        ): Optional<StreamDescriptor> {
            if (
                message.state?.type != null &&
                    message.state?.type == AirbyteStateMessage.AirbyteStateType.STREAM
            ) {
                val streamDescriptor: StreamDescriptor? = message.state?.stream?.streamDescriptor
                if (Strings.isNullOrEmpty(streamDescriptor?.namespace)) {
                    return Optional.of(
                        StreamDescriptor()
                            .withName(
                                streamDescriptor?.name,
                            )
                            .withNamespace(defaultNamespace),
                    )
                }
                return streamDescriptor?.let { Optional.of(it) } ?: Optional.empty()
            }
            return Optional.empty()
        }
    }
}
