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
    private val stateKeyClient: StateKeyClient,
    private val stateStore: StateStore,
    private val statePublisher: StatePublisher,
) {
    private val iterationDuration: Duration = 30.seconds
    private lateinit var job: Job

    fun run() = runBlocking{
        job = launch {
            while (true) {
                delay(iterationDuration)

                val completeKeys = stateWatermarkStore.getCompleteStateKeys()

                while (true) {
                    val entry = stateStore.states.firstEntry()

                    val keys = listOf<StateKey>() // partitions
                    if (keys.all { completeKeys.contains(it) }) {
                        val polled = stateStore.states.pollFirstEntry()
                        statePublisher.publish(polled.value)
                    }

                }
            }
        }
    }

    suspend fun disable() = job.cancelAndJoin()

}
