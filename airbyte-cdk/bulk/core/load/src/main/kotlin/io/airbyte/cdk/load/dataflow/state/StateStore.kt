/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.stats.StateStatsEnricher
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentSkipListMap
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

@Singleton
class StateStore(
    private val keyClient: StateKeyClient,
    private val histogramStore: StateHistogramStore,
    private val stateStatsEnricher: StateStatsEnricher,
    private val catalog: DestinationCatalog,
) {
    private val log = KotlinLogging.logger {}

    private enum class Mode {
        GLOBAL,
        STREAM
    }

    private val mode = AtomicReference<Mode?>(null)

    private val globalStates = ConcurrentSkipListMap<StateKey, CheckpointMessage>()
    private val globalNextIndex = AtomicLong(1L)

    private data class StreamState(
        val queue: ConcurrentSkipListMap<StateKey, CheckpointMessage> = ConcurrentSkipListMap(),
        val nextIndex: AtomicLong = AtomicLong(1L),
    )

    private val streamStates = ConcurrentHashMap<DestinationStream.Descriptor, StreamState>()
    private val mappedDescriptors by lazy {
        catalog.streams.associate { it.unmappedDescriptor to it.mappedDescriptor }
    }

    fun accept(msg: CheckpointMessage) {
        val key = keyClient.getStateKey(msg)
        val scope =
            when (msg) {
                is GlobalCheckpoint,
                is GlobalSnapshotCheckpoint -> StateScope.Global
                is StreamCheckpoint ->
                    StateScope.Stream(mappedDescriptor(msg.checkpoint.unmappedDescriptor))
            }

        val stats =
            requireNotNull(msg.sourceStats) {
                "sourceStats must be set with recordCount for state message id=${key.id}"
            }
        histogramStore.acceptExpectedCounts(scope, key, stats.recordCount)

        when (msg) {
            is GlobalCheckpoint,
            is GlobalSnapshotCheckpoint -> {
                enforceMode(Mode.GLOBAL)
                globalStates[key] = msg
            }
            is StreamCheckpoint -> {
                enforceMode(Mode.STREAM)
                val desc = msg.checkpoint.unmappedDescriptor
                val state = streamStates.computeIfAbsent(desc) { StreamState() }
                state.queue[key] = msg
            }
        }
    }

    fun getNextComplete(): CheckpointMessage? {
        return when (mode.get()) {
            null -> {
                null
            }
            Mode.GLOBAL -> {
                val head = globalStates.firstKeyOrNull() ?: return noGlobalToFlush()
                val expected = globalNextIndex.get()
                if (head.id != expected) {
                    return null
                }
                if (!histogramStore.isComplete(StateScope.Global, head)) {
                    return null
                }

                val msg = globalStates.remove(head)!!
                globalNextIndex.incrementAndGet()
                histogramStore.remove(StateScope.Global, head)
                stateStatsEnricher.enrich(msg, head)
            }
            Mode.STREAM -> {
                var stateToEmit: Pair<DestinationStream.Descriptor, StateKey>? = null
                for ((desc, stateMessages) in streamStates.entries) {
                    val head = stateMessages.queue.firstKeyOrNull() ?: continue
                    val expected = stateMessages.nextIndex.get()
                    if (head.id != expected) {
                        continue
                    }
                    if (
                        !histogramStore.isComplete(StateScope.Stream(mappedDescriptor(desc)), head)
                    ) {
                        continue
                    }
                    if (stateToEmit == null) {
                        stateToEmit = desc to head
                    }
                }

                if (stateToEmit == null) return null

                val (desc, head) = stateToEmit
                val st = streamStates[desc] ?: return null
                val msg = st.queue.remove(head) ?: return null

                st.nextIndex.incrementAndGet()
                histogramStore.remove(StateScope.Stream(mappedDescriptor(desc)), head)
                stateStatsEnricher.enrich(msg, head)
            }
        }
    }

    fun hasStates(): Boolean {
        return when (mode.get()) {
            null -> false
            Mode.GLOBAL -> globalStates.isNotEmpty()
            Mode.STREAM -> streamStates.values.any { it.queue.isNotEmpty() }
        }
    }

    fun logStateInfo() {
        when (mode.get()) {
            null -> {
                log.info {
                    "State diagnostic information: no states enqueued (mode not chosen yet)"
                }
            }
            Mode.GLOBAL -> {
                val head = globalStates.firstKeyOrNull()
                if (head == null) {
                    log.info { "State diagnostic information [GLOBAL]: no states enqueued" }
                    return
                }
                val state = globalStates[head]
                val expected = globalNextIndex.get()

                val sb =
                    StringBuilder("State diagnostic information [GLOBAL]:")
                        .append("\nFirst key: $head (state: $state)")
                when {
                    head.id != expected ->
                        sb.append("\n  • Waiting for index $expected (head is ${head.id})")
                    !histogramStore.isComplete(StateScope.Global, head) ->
                        sb.append(
                            "\n  • Incomplete: ${histogramStore.whyIsStateIncomplete(StateScope.Global, head)}"
                        )
                    else -> sb.append("\n  • Head is complete and ready to flush")
                }
                log.info { sb.toString() }
            }
            Mode.STREAM -> {
                if (streamStates.isEmpty()) {
                    log.info { "State diagnostic information [STREAM]: no states enqueued" }
                    return
                }
                val sb = StringBuilder("State diagnostic information [STREAM] (by descriptor):")
                for ((desc, st) in streamStates.entries) {
                    val head = st.queue.firstKeyOrNull()
                    if (head == null) {
                        sb.append("\n- descriptor=$desc: no states enqueued")
                        continue
                    }
                    val state = st.queue[head]
                    val expected = st.nextIndex.get()

                    sb.append("\n- descriptor=$desc first key: $head (state: $state)")
                    when {
                        head.id != expected ->
                            sb.append("\n  • Waiting for index $expected (head is ${head.id})")
                        !histogramStore.isComplete(
                            StateScope.Stream(mappedDescriptor(desc)),
                            head
                        ) ->
                            sb.append(
                                "\n  • Incomplete: ${histogramStore.whyIsStateIncomplete(StateScope.Stream(mappedDescriptor(desc)), head)}"
                            )
                        else -> sb.append("\n  • Head is complete and ready to flush")
                    }
                }
                log.info { sb.toString() }
            }
        }
    }

    private fun enforceMode(desired: Mode) {
        val cur = mode.get()
        if (cur == null) {
            if (!mode.compareAndSet(null, desired)) {
                val after = mode.get()
                if (after != desired) {
                    error(
                        "Mixed state types in a single sync are not allowed. Existing=$after, incoming=$desired"
                    )
                }
            }
        } else if (cur != desired) {
            error(
                "Mixed state types in a single sync are not allowed. Existing=$cur, incoming=$desired"
            )
        }
    }

    private fun mappedDescriptor(
        unmappedDescriptor: DestinationStream.Descriptor
    ): DestinationStream.Descriptor =
        mappedDescriptors[unmappedDescriptor]
            ?: unmappedDescriptor.also {
                log.warn {
                    "No mapped descriptor found for unmapped descriptor ${unmappedDescriptor.toPrettyString()}; using it as-is."
                }
            }

    private fun noGlobalToFlush(): Nothing? {
        return null
    }

    private fun <K, V> ConcurrentSkipListMap<K, V>.firstKeyOrNull(): K? =
        try {
            this.firstKey()
        } catch (_: NoSuchElementException) {
            null
        }
}
