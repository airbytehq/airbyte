/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.asProtocolStreamDescriptor
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference
import org.apache.mina.util.ConcurrentHashSet

/**
 * [StreamStatusManager] emits [AirbyteStreamStatusTraceMessage]s in response to [Feed] activity
 * events, via [notifyStarting], [notifyComplete] and [notifyFailure].
 */
class StreamStatusManager(
    feeds: List<Feed>,
    private val emit: (AirbyteStreamStatusTraceMessage) -> Unit,
) {
    private val streamStates: Map<StreamIdentifier, StreamState> =
        feeds
            .flatMap { feed: Feed -> feed.streams.map { it.id to feed } }
            .groupBy({ it.first }, { it.second })
            .mapValues { (id: StreamIdentifier, feeds: List<Feed>) ->
                StreamState(id, feeds.toSet())
            }

    /**
     * Notify that the [feed] is about to start running.
     *
     * Emits Airbyte TRACE messages of type STATUS accordingly. Safe to call even if
     * [notifyStarting], [notifyComplete] or [notifyFailure] have been called before.
     */
    fun notifyStarting(feed: Feed) {
        handle(feed) { it.onStarting() }
    }

    /**
     * Notify that the [feed] has completed running.
     *
     * Emits Airbyte TRACE messages of type STATUS accordingly. Idempotent. Safe to call even if
     * [notifyStarting] hasn't been called previously.
     */
    fun notifyComplete(feed: Feed) {
        handle(feed) { it.onComplete(feed) }
    }

    /**
     * Notify that the [feed] has stopped running due to a failure.
     *
     * Emits Airbyte TRACE messages of type STATUS accordingly. Idempotent. Safe to call even if
     * [notifyStarting] hasn't been called previously.
     */
    fun notifyFailure(feed: Feed) {
        handle(feed) { it.onFailure(feed) }
    }

    private fun handle(feed: Feed, notification: (StreamState) -> List<AirbyteStreamStatus>) {
        for (stream in feed.streams) {
            val streamState: StreamState = streamStates[stream.id] ?: continue
            for (statusToEmit: AirbyteStreamStatus in notification(streamState)) {
                emit(
                    AirbyteStreamStatusTraceMessage()
                        .withStreamDescriptor(stream.id.asProtocolStreamDescriptor())
                        .withStatus(statusToEmit)
                )
            }
        }
    }

    data class StreamState(
        val id: StreamIdentifier,
        val feeds: Set<Feed>,
        val state: AtomicReference<State> = AtomicReference(State.PENDING),
        val stoppedFeeds: ConcurrentHashSet<Feed> = ConcurrentHashSet(),
        val numStoppedFeeds: AtomicInteger = AtomicInteger()
    ) {
        fun onStarting(): List<AirbyteStreamStatus> =
            if (state.compareAndSet(State.PENDING, State.SUCCESS)) {
                listOf(AirbyteStreamStatus.STARTED)
            } else {
                emptyList()
            }

        fun onComplete(feed: Feed): List<AirbyteStreamStatus> =
            onStarting() + // ensure the state is not PENDING
            run {
                    if (!finalStop(feed)) {
                        return@run emptyList()
                    }
                    // At this point, we just stopped the last feed for this stream.
                    // Transition to DONE.
                    if (state.compareAndSet(State.SUCCESS, State.DONE)) {
                        listOf(AirbyteStreamStatus.COMPLETE)
                    } else if (state.compareAndSet(State.FAILURE, State.DONE)) {
                        listOf(AirbyteStreamStatus.INCOMPLETE)
                    } else {
                        emptyList() // this should never happen
                    }
                }

        fun onFailure(feed: Feed): List<AirbyteStreamStatus> =
            onStarting() + // ensure the state is not PENDING
            run {
                    state.compareAndSet(State.SUCCESS, State.FAILURE)
                    if (!finalStop(feed)) {
                        return@run emptyList()
                    }
                    // At this point, we just stopped the last feed for this stream.
                    // Transition from FAILURE to DONE.
                    if (state.compareAndSet(State.FAILURE, State.DONE)) {
                        listOf(AirbyteStreamStatus.INCOMPLETE)
                    } else {
                        emptyList() // this should never happen
                    }
                }

        private fun finalStop(feed: Feed): Boolean {
            if (!stoppedFeeds.add(feed)) {
                // This feed was stopped before.
                return false
            }
            // True if and only if this feed was stopped and all others were already stopped.
            return numStoppedFeeds.incrementAndGet() == feeds.size
        }
    }

    enum class State {
        PENDING,
        SUCCESS,
        FAILURE,
        DONE,
    }
}
