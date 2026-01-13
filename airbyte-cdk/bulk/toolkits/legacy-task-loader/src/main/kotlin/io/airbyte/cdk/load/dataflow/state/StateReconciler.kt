/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage
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
    @Named("stateReconcilerScope") private val scope: CoroutineScope,
    @Named("stateReconcilerInterval") interval: Duration?, // only java durations can be injected
) {
    // allow overriding this for test purposes
    private val interval = interval?.toKotlinDuration() ?: 30.seconds
    private lateinit var job: Job

    fun run() {
        job =
            scope.launch {
                while (true) {
                    delay(interval)
                    flushCompleteStates()
                    flushEmittedStats()
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
