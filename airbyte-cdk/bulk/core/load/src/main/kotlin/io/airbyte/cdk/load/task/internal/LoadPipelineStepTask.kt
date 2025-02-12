/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchEndOfStream
import io.airbyte.cdk.load.pipeline.BatchStateUpdate
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import io.airbyte.cdk.load.pipeline.PipelineFlushStrategy
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.fold

data class RangeState<S>(
    val state: S,
    val checkpointCounts: MutableMap<CheckpointId, Long> = mutableMapOf(),
    val inputCount: Long = 0,
)

/** A long-running task that actually implements a load pipeline step. */
class LoadPipelineStepTask<S : AutoCloseable, K1 : WithStream, T, K2 : WithStream, U : Any>(
    private val batchAccumulator: BatchAccumulator<S, K1, T, U>,
    private val inputFlow: Flow<Reserved<PipelineEvent<K1, T>>>,
    private val batchUpdateQueue: QueueWriter<BatchUpdate>,
    private val outputPartitioner: OutputPartitioner<K1, T, K2, U>?,
    private val outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
    private val flushStrategy: PipelineFlushStrategy?,
    private val part: Int,
) : Task {
    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() {
        inputFlow.fold(mutableMapOf<K1, RangeState<S>>()) { stateStore, reservation ->
            try {
                when (val input = reservation.value) {
                    is PipelineMessage -> {
                        // Fetch and update the local state associated with the current batch.
                        val state =
                            stateStore
                                .getOrPut(input.key) {
                                    RangeState(
                                        batchAccumulator.start(input.key, part),
                                    )
                                }
                                .let { it.copy(inputCount = it.inputCount + 1) }
                        val (newState, output) =
                            batchAccumulator.accept(
                                input.value,
                                state.state,
                            )
                        reservation.release() // TODO: Accumulate and release when persisted
                        input.checkpointCounts.forEach {
                            state.checkpointCounts.merge(it.key, it.value) { old, new -> old + new }
                        }

                        // If the accumulator did not produce a result, check if we should flush.
                        // If so, use the result of a finish call as the output.
                        val finalOutput =
                            output
                                ?: if (flushStrategy?.shouldFlush(state.inputCount) == true) {
                                    batchAccumulator.finish(newState)
                                } else {
                                    null
                                }

                        if (finalOutput != null) {
                            // Publish the emitted output and evict the state.
                            handleOutput(input.key, state.checkpointCounts, finalOutput)
                            stateStore.remove(input.key)
                        } else {
                            // If there's no output yet, just update the local state.
                            stateStore[input.key] = RangeState(newState, state.checkpointCounts)
                        }
                        stateStore
                    }
                    is PipelineEndOfStream -> {
                        // Give any key associated with the stream a chance to finish
                        val keysToRemove = stateStore.keys.filter { it.stream == input.stream }
                        keysToRemove.forEach { key ->
                            stateStore.remove(key)?.let { stored ->
                                val output = batchAccumulator.finish(stored.state)
                                handleOutput(key, stored.checkpointCounts, output)
                            }
                        }

                        outputQueue?.broadcast(PipelineEndOfStream(input.stream))
                        batchUpdateQueue.publish(BatchEndOfStream(input.stream))

                        stateStore
                    }
                }
            } catch (t: Throwable) {
                // Close the local state associated with the current batch.
                stateStore.values
                    .map { runCatching { it.state.close() } }
                    .forEach { it.getOrThrow() }
                throw t
            }
        }
    }

    private suspend fun handleOutput(
        inputKey: K1,
        checkpointCounts: Map<CheckpointId, Long>,
        output: U
    ) {

        // Only publish the output if there's a next step.
        outputQueue?.let {
            val outputKey = outputPartitioner!!.getOutputKey(inputKey, output)
            val message = PipelineMessage(checkpointCounts, outputKey, output)
            val outputPart = outputPartitioner.getPart(outputKey, it.partitions)
            it.publish(message, outputPart)
        }

        // If the output contained a global batch state, publish an update.
        if (output is WithBatchState && output.state.isPersisted()) {
            val update =
                BatchStateUpdate(
                    stream = inputKey.stream,
                    checkpointCounts = checkpointCounts,
                    state = output.state
                )
            batchUpdateQueue.publish(update)
        }
    }
}
