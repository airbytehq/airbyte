/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.time.Duration
import kotlin.time.Duration.Companion.seconds
import kotlin.time.toKotlinDuration
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/** At an interval it checks for any complete states and flushes them to the platform. */
@Singleton
class StateReconciler(
    private val stateStore: StateStore,
    private val emittedStatsStore: EmittedStatsStore,
    private val consumer: OutputConsumer,
    private val watermarkTracker: MessageWatermarkTracker,
    @Named("stateReconcilerScope") private val scope: CoroutineScope,
    @Named("stateReconcilerInterval") interval: Duration?, // only java durations can be injected
    @Named("sourceStallThreshold") sourceStallThreshold: Duration?, // threshold for detecting stalled sources
) {
    private val log = KotlinLogging.logger {}

    // allow overriding this for test purposes
    private val interval = interval?.toKotlinDuration() ?: 30.seconds
    private val stallThresholdMillis = sourceStallThreshold?.toMillis() ?: (10 * 60 * 1000L) // default 10 minutes
    private lateinit var job: Job

    fun run() {
        job =
            scope.launch {
                while (true) {
                    delay(interval)
                    checkForStalledSource()
                    flushCompleteStates()
                    flushEmittedStats()
                }
            }
    }

    private fun checkForStalledSource() {
        if (watermarkTracker.isStalled(stallThresholdMillis)) {
            val minutesSinceLastMessage = (watermarkTracker.getMillisSinceLastMessage() ?: 0) / (60 * 1000)
            log.warn {
                "WARNING: Source appears to be stalled. No messages received in $minutesSinceLastMessage minutes. " +
                "The destination is waiting for data from the source. " +
                "This is likely a source-side issue, not a destination issue. " +
                "Please check the source connector logs for errors or signs of being stuck."
            }
        }
    }

    fun flushCompleteStates() {
        var complete = stateStore.getNextComplete()
        while (complete != null) {
            publish(complete.asProtocolMessage())
            complete = stateStore.getNextComplete()
        }
    }

    fun flushEmittedStats() {
        val stats = emittedStatsStore.getStats()
        stats?.let { stats.forEach(::publish) }
    }

    fun publish(msg: AirbyteMessage) {
        consumer.accept(msg)
    }

    suspend fun disable() = job.cancelAndJoin()
}
