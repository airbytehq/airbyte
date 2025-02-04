/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.RangeSet
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
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.fold

/** A long-running task that actually implements a load pipeline step. */
class LoadPipelineStepTask<S : AutoCloseable, K1 : WithStream, T, K2 : WithStream, U : Any>(
    private val batchAccumulator: BatchAccumulator<K1, S, T, U>,
    private val inputFlow: Flow<PipelineEvent<K1, T>>,
    private val batchUpdateQueue: QueueWriter<BatchUpdate>,
    private val outputPartitioner: OutputPartitioner<K1, T, K2, U>,
    private val outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
    private val part: Int,
) : Task {
    override val terminalCondition: TerminalCondition = OnEndOfSync

    inner class RangeState(
        val state: S,
        val indexRange: RangeSet<Long>? = null,
    )

    override suspend fun execute() {
        inputFlow.fold(mutableMapOf<K1, RangeState>()) { stateStore, input ->
            try {
                when (input) {
                    is PipelineMessage -> {
                        // Fetch and update the local state associated with the current batch.
                        val state =
                            stateStore.getOrPut(input.key) {
                                RangeState(
                                    batchAccumulator.start(input.key, part),
                                )
                            }
                        val (newState, output) =
                            batchAccumulator.accept(
                                input.value,
                                state.state,
                            )
                        val nextRange = state.indexRange.with(input.indexRange)

                        if (output != null) {
                            // Publish the emitted output and evict the state.
                            handleOutput(input.key, nextRange, output)
                            stateStore.remove(input.key)
                        } else {
                            // If there's no output yet, just update the local state.
                            stateStore[input.key] = RangeState(newState, nextRange)
                        }
                        stateStore
                    }
                    is PipelineEndOfStream -> {
                        // Give any key associated with the stream a chance to finish
                        val keysToRemove = stateStore.keys.filter { it.stream == input.stream }
                        keysToRemove.forEach { key ->
                            stateStore.remove(key)?.let { stored ->
                                val output = batchAccumulator.finish(stored.state)
                                handleOutput(key, stored.indexRange!!, output)
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

    private suspend fun handleOutput(inputKey: K1, nextRange: RangeSet<Long>, output: U) {

        // Only publish the output if there's a next step.
        outputQueue?.let {
            val outputKey = outputPartitioner.getOutputKey(inputKey, output)
            val message = PipelineMessage(nextRange, outputKey, output)
            val outputPart = outputPartitioner.getPart(outputKey, it.partitions)
            it.publish(message, outputPart)
        }

        // If the output contained a global batch state, publish an update.
        if (output is WithBatchState) {
            val update =
                BatchStateUpdate(
                    stream = inputKey.stream,
                    indexRange = nextRange,
                    state = output.state
                )
            batchUpdateQueue.publish(update)
        }
    }

    private fun RangeSet<Long>?.with(other: RangeSet<Long>): RangeSet<Long> {
        return if (this == null) {
            other
        } else {
            this.addAll(other)
            this
        }
    }
}
