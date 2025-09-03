/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.output.OutputConsumer
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
    private val consumer: OutputConsumer,
    @Named("stateReconciliationInterval")
    reconciliationInterval: Duration?, // only java durations can be injected
) {
    // allow overriding this for test purposes
    private val reconciliationInterval = reconciliationInterval?.toKotlinDuration() ?: 30.seconds
    private lateinit var job: Job

    fun run(scope: CoroutineScope) {
        job =
            scope.launch {
                while (true) {
                    delay(reconciliationInterval)
                    flushCompleteStates()
                }
            }
    }

    fun flushCompleteStates() {
        var complete = stateStore.getNextComplete()
        while (complete != null) {
            publish(complete)
            complete = stateStore.getNextComplete()
        }
    }

    fun publish(msg: CheckpointMessage) {
        consumer.accept(msg.asProtocolMessage())
    }

    suspend fun disable() = job.cancelAndJoin()
}
