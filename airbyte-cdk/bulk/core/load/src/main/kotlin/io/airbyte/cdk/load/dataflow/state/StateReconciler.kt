/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import jakarta.inject.Singleton
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

@Singleton
class StateReconciler(
    private val stateWatermarkStore: StateWatermarkStore,
    private val stateStore: StateStore,
    private val statePublisher: StatePublisher,
) {
    private val iterationDuration: Duration = 30.seconds
    private lateinit var job: Job

    fun run() = runBlocking {
        job = launch {
            while (true) {
                delay(iterationDuration)

                flushStates()
            }
        }
    }

    fun flushStates() {
        while (true) {
            val key = stateStore.states.firstKey()
            val complete = stateWatermarkStore.isComplete(key)
            if (complete) {
                statePublisher.publish(stateStore.remove(key))
            } else {
                break
            }
        }
    }

    suspend fun disable() = job.cancelAndJoin()
}
