/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.message.Batch
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
    private val inputFlow: Flow<PipelineEvent<K1, T>>,
    private val batchUpdateQueue: QueueWriter<BatchUpdate>,
    private val outputPartitioner: OutputPartitioner<K1, T, K2, U>?,
    private val outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
    private val flushStrategy: PipelineFlushStrategy?,
    private val part: Int,
) : Task {
    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() {
        inputFlow.fold(mutableMapOf<K1, RangeState<S>>()) { stateStore, input ->
            try {
                when (input) {
                    is PipelineMessage -> {
                        // Get or create the accumulator state associated w/ the input key.
                        val state =
                            stateStore
                                .getOrPut(input.key) {
                                    RangeState(
                                        batchAccumulator.start(input.key, part),
                                    )
                                }
                                .let { it.copy(inputCount = it.inputCount + 1) }

                        // Accumulate the input and get the new state and output.
                        val (newStateMaybe, outputMaybe) =
                            batchAccumulator.accept(
                                input.value,
                                state.state,
                            )
                        /** TODO: Make this impossible at the return type level */
                        if (newStateMaybe == null && outputMaybe == null) {
                            throw IllegalStateException(
                                "BatchAccumulator must return a new state or an output"
                            )
                        }

                        // Update bookkeeping metadata
                        input.checkpointCounts.forEach {
                            state.checkpointCounts.merge(it.key, it.value) { old, new -> old + new }
                        }

                        // Finalize the state and output
                        val (finalState, finalOutput) =
                            if (outputMaybe == null) {
                                // Possibly force an output (and if so, discard the state)
                                if (flushStrategy?.shouldFlush(state.inputCount) == true) {
                                    val finalOutput = batchAccumulator.finish(newStateMaybe!!)
                                    Pair(null, finalOutput)
                                } else {
                                    Pair(newStateMaybe, null)
                                }
                            } else {
                                // Otherwise, just use what we were given
                                Pair(newStateMaybe, outputMaybe)
                            }

                        // Publish the output if there is one & reset the input count
                        val inputCount =
                            if (finalOutput != null) {
                                // Publish the emitted output and evict the state.
                                handleOutput(input.key, state.checkpointCounts, finalOutput)
                                state.checkpointCounts.clear()
                                0
                            } else {
                                state.inputCount
                            }

                        // Update the state if `accept` returned a new state, otherwise evict.
                        if (finalState != null) {
                            // If accept returned a new state, update the state store.
                            stateStore[input.key] =
                                state.copy(state = finalState, inputCount = inputCount)
                        } else {
                            stateStore.remove(input.key)
                        }

                        input
                            .postProcessingCallback() // TODO: Accumulate and release when persisted

                        stateStore
                    }
                    is PipelineEndOfStream -> {
                        // Give any key associated with the stream a chance to finish
                        val keysToRemove = stateStore.keys.filter { it.stream == input.stream }
                        keysToRemove.forEach { key ->
                            stateStore.remove(key)?.let { stored ->
                                if (stored.inputCount > 0) {
                                    val output = batchAccumulator.finish(stored.state)
                                    handleOutput(key, stored.checkpointCounts, output)
                                }
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
            val message = PipelineMessage(checkpointCounts.toMap(), outputKey, output)
            val outputPart = outputPartitioner.getPart(outputKey, it.partitions)
            it.publish(message, outputPart)
        }

        // If the output contained a global batch state, publish an update.
        if (output is WithBatchState && output.state.isPersisted()) {
            val update =
                BatchStateUpdate(
                    stream = inputKey.stream,
                    checkpointCounts = checkpointCounts.toMap(),
                    state = output.state
                )
            batchUpdateQueue.publish(update)
        }
    }
}
